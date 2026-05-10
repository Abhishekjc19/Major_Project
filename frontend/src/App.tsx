import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Map as MapIcon, Bell, Settings, Filter, Bus as BusIcon, Info, Plus, Minus, UserCheck, History, ChevronRight, MapPin, CreditCard, ShieldAlert, PackageSearch, MessageSquare, AlertTriangle, Send, Clock, X, LogOut } from 'lucide-react';
import { io, Socket } from 'socket.io-client';
import { Bus, RideHistory, LostItemReport } from './types';
import { MOCK_HISTORY, MOCK_REPORTS } from './constants';
import { BusCard } from './components/BusCard';
import { BusDetails } from './components/BusDetails';
import { cn } from './lib/utils';

// Backend URLs from environment
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';

let socket: Socket | null = null;

type Tab = 'buses' | 'map' | 'history' | 'safety';

interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: 'passenger' | 'conductor' | 'admin';
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [buses, setBuses] = useState<Bus[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBus, setSelectedBus] = useState<Bus | null>(null);
  const [activeFilter, setActiveFilter] = useState<'all' | 'available' | 'partial' | 'full'>('all');
  const [isConductorMode, setIsConductorMode] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('buses');

  // History Filters
  const [historySearch, setHistorySearch] = useState('');
  const [historyDateFilter, setHistoryDateFilter] = useState('');

  // SOS State
  const [sosActive, setSosActive] = useState(false);
  const [sosCountdown, setSosCountdown] = useState(5);

  // Chat State
  const [activeChatReport, setActiveChatReport] = useState<LostItemReport | null>(null);
  const [trackingBus, setTrackingBus] = useState<Bus | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<{text: string, sender: 'user' | 'conductor'}[]>([]);

  // Load stored auth token and authenticate
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('authUser');

    if (token && user) {
      try {
        const userData = JSON.parse(user);
        setAuthUser(userData);
        setIsAuthenticated(true);
        initializeSocket(token);
      } catch (error) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
      }
    }
  }, []);

  // Transform bus data from backend format to frontend format
  const transformBus = (busData: any): Bus => ({
    id: busData.id,
    routeNumber: busData.route_number,
    destination: busData.destination,
    currentOccupancy: busData.current_occupancy || 0,
    totalCapacity: busData.capacity || 50,
    status: busData.status || 'available',
    nextStop: 'Central Station',
    stops: [],
    lastUpdated: busData.last_updated || 'Just now',
    predictedOccupancy: [],
  });

  // Initialize Socket.IO connection
  const initializeSocket = (token: string) => {
    if (socket?.connected) return;

    socket = io(SOCKET_URL, {
      auth: {
        token,
      },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    socket.on('buses:init', (initialBuses: any[]) => {
      console.log('Received buses:init with', initialBuses.length, 'buses');
      setBuses(initialBuses.map(transformBus));
    });

    socket.on('bus:update', (updatedBus: any) => {
      const transformedBus = transformBus(updatedBus);
      setBuses(prev => prev.map(b => b.id === transformedBus.id ? transformedBus : b));
      if (selectedBus?.id === transformedBus.id) {
        setSelectedBus(transformedBus);
      }
    });

    socket.on('connect', () => {
      console.log('Connected to backend, requesting buses');
      socket?.emit('buses:request-update');
    });

    socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    // If already connected, emit the request immediately
    if (socket.connected) {
      socket.emit('buses:request-update');
    }

    return () => {
      socket?.off('buses:init');
      socket?.off('bus:update');
    };
  };

  // Handle login
  const handleLogin = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail, password: loginPassword }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      const userData = data.user;

      localStorage.setItem('authToken', data.token);
      localStorage.setItem('authUser', JSON.stringify(userData));

      setAuthUser(userData);
      setIsAuthenticated(true);
      setLoginEmail('');
      setLoginPassword('');

      initializeSocket(data.token);
    } catch (error: any) {
      alert('Login failed: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    setAuthUser(null);
    setIsAuthenticated(false);
    if (socket) {
      socket.disconnect();
      socket = null;
    }
    setBuses([]);
  };

  useEffect(() => {
    if (!socket || !isAuthenticated) return;

    socket.on('buses:init', (initialBuses: any[]) => {
      setBuses(initialBuses.map(transformBus));
    });

    socket.on('bus:update', (updatedBus: any) => {
      const transformedBus = transformBus(updatedBus);
      setBuses(prev => prev.map(b => b.id === transformedBus.id ? transformedBus : b));
      if (selectedBus?.id === transformedBus.id) {
        setSelectedBus(transformedBus);
      }
    });

    return () => {
      socket?.off('buses:init');
      socket?.off('bus:update');
    };
  }, [selectedBus, isAuthenticated]);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (sosActive && sosCountdown > 0) {
      timer = setInterval(() => setSosCountdown(prev => prev - 1), 1000);
    } else if (sosCountdown === 0) {
      // SOS Triggered
      console.log("SOS TRIGGERED");
    }
    return () => clearInterval(timer);
  }, [sosActive, sosCountdown]);

  const filteredBuses = useMemo(() => {
    return buses.filter(bus => {
      const matchesSearch = (bus.routeNumber || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (bus.destination || '').toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = activeFilter === 'all' || bus.status === activeFilter;
      return matchesSearch && matchesFilter;
    });
  }, [buses, searchQuery, activeFilter]);

  const filteredHistory = useMemo(() => {
    return MOCK_HISTORY.filter(ride => {
      const matchesSearch = ride.routeNumber.toLowerCase().includes(historySearch.toLowerCase()) ||
                          ride.from.toLowerCase().includes(historySearch.toLowerCase()) ||
                          ride.to.toLowerCase().includes(historySearch.toLowerCase());
      const matchesDate = !historyDateFilter || ride.date === historyDateFilter;
      return matchesSearch && matchesDate;
    });
  }, [historySearch, historyDateFilter]);

  const handleSellTicket = (busId: string) => {
    if (!socket?.connected) {
      alert('Not connected to server');
      return;
    }
    socket.emit('ticket:sold', { busId, count: 1 });
  };

  const handleCancelTicket = (busId: string) => {
    if (!socket?.connected) {
      alert('Not connected to server');
      return;
    }
    socket.emit('ticket:cancelled', { busId, count: 1 });
  };

  const handleSendMessage = () => {
    if (!chatMessage.trim()) return;
    setChatMessages(prev => [...prev, { text: chatMessage, sender: 'user' }]);
    setChatMessage('');
    
    // Simulate conductor response
    setTimeout(() => {
      setChatMessages(prev => [...prev, { 
        text: "I've checked the lost items log. We'll update your report status if it's found.", 
        sender: 'conductor' 
      }]);
    }, 1500);
  };

  const renderHistory = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* History Filters */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by route or place..."
            value={historySearch}
            onChange={(e) => setHistorySearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-50 border-none rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-primary/10"
          />
        </div>
        <div className="flex space-x-2">
          <input
            type="date"
            value={historyDateFilter}
            onChange={(e) => setHistoryDateFilter(e.target.value)}
            className="flex-1 px-4 py-3 bg-slate-50 border-none rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-primary/10"
          />
          <button 
            onClick={() => { setHistorySearch(''); setHistoryDateFilter(''); }}
            className="px-4 py-3 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold uppercase"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-slate-900">Ride Summary</h3>
          <div className="bg-brand-primary/10 px-3 py-1 rounded-full">
            <span className="text-xs font-bold text-brand-primary uppercase">{filteredHistory.length} Rides</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-50 p-4 rounded-2xl">
            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Total Spent</p>
            <p className="text-xl font-display font-bold text-slate-900">$12.50</p>
          </div>
          <div className="bg-slate-50 p-4 rounded-2xl">
            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Avg. Occupancy</p>
            <p className="text-xl font-display font-bold text-slate-900">24%</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Recent Activity</h3>
        {filteredHistory.map((ride) => (
          <div 
            key={ride.id} 
            className="glass-card p-5 rounded-3xl relative overflow-hidden group hover:border-brand-primary/30 transition-colors cursor-pointer"
            onClick={() => {
              const liveBus = buses.find(b => b.routeNumber === ride.routeNumber);
              if (liveBus) {
                setTrackingBus(liveBus);
                setChatMessages([{ text: `Hello, I was on your bus ${ride.routeNumber} earlier today. I think I left my wallet. Can you check?`, sender: 'user' }]);
              } else {
                // Fallback if bus is not currently live
                alert(`Bus ${ride.routeNumber} is not currently active. Please report this in the Safety tab.`);
              }
            }}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-900 font-display font-bold">
                  {ride.routeNumber}
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{ride.date}</p>
                  <p className="text-sm font-bold text-slate-900">{ride.time}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-brand-primary">{ride.fare}</p>
                <div className="flex items-center justify-end text-[10px] text-slate-400 mt-1">
                  <CreditCard className="w-3 h-3 mr-1" />
                  <span>Wallet</span>
                </div>
              </div>
            </div>

            <div className="space-y-2 relative pl-4">
              <div className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-slate-100" />
              <div className="flex items-center text-slate-600">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-300 absolute left-[-0.5px] top-1.5" />
                <span className="text-xs font-medium ml-2">From: <span className="text-slate-900">{ride.from}</span></span>
              </div>
              <div className="flex items-center text-slate-600">
                <div className="w-1.5 h-1.5 rounded-full bg-brand-primary absolute left-[-0.5px] bottom-1.5" />
                <span className="text-xs font-medium ml-2">To: <span className="text-slate-900 font-bold">{ride.to}</span></span>
              </div>
            </div>
            
            <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <ChevronRight className="w-5 h-5 text-slate-300" />
            </div>
          </div>
        ))}
        {filteredHistory.length === 0 && (
          <div className="text-center py-10 text-slate-400">
            <Clock className="w-10 h-10 mx-auto mb-2 opacity-20" />
            <p className="text-sm">No rides found for these filters.</p>
          </div>
        )}
      </div>
    </motion.div>
  );

  const renderSafety = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-8"
    >
      {/* SOS Section */}
      <section className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-xl text-center relative overflow-hidden">
        <div className="relative z-10">
          <div className="w-20 h-20 bg-brand-danger/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShieldAlert className={cn("w-10 h-10 text-brand-danger", sosActive && "animate-ping")} />
          </div>
          <h3 className="text-2xl font-display font-bold text-slate-900 mb-2">Emergency SOS</h3>
          <p className="text-slate-500 text-sm mb-8 px-4">
            Press the button below to alert emergency services and the bus conductor immediately.
          </p>
          
          <button 
            onClick={() => {
              if (sosActive) {
                setSosActive(false);
                setSosCountdown(5);
              } else {
                setSosActive(true);
              }
            }}
            className={cn(
              "w-full py-6 rounded-3xl font-bold text-xl transition-all shadow-2xl",
              sosActive 
                ? "bg-slate-900 text-white" 
                : "bg-brand-danger text-white shadow-brand-danger/30 hover:scale-[1.02]"
            )}
          >
            {sosActive ? `Cancel SOS (${sosCountdown}s)` : 'ACTIVATE SOS'}
          </button>
        </div>
        {sosActive && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-brand-danger/5 animate-pulse pointer-events-none" 
          />
        )}
      </section>

      {/* Lost & Found Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Lost & Found</h3>
          <button className="text-xs font-bold text-brand-primary flex items-center">
            <Plus className="w-3 h-3 mr-1" /> New Report
          </button>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center">
            <PackageSearch className="w-5 h-5 text-slate-400 mr-2" />
            <span className="text-sm font-bold text-slate-700">Recent Reports</span>
          </div>
          <div className="divide-y divide-slate-100">
            {MOCK_REPORTS.map(report => (
              <div 
                key={report.id} 
                className="p-4 hover:bg-slate-50 transition-colors cursor-pointer group"
                onClick={() => {
                  setActiveChatReport(report);
                  setChatMessages([{ text: `Hello, I lost my ${report.itemName} on bus ${report.busId}. Any updates?`, sender: 'user' }]);
                }}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-bold text-slate-900">{report.itemName}</h4>
                    <p className="text-[10px] text-slate-500">Bus {report.busId} • {report.date}</p>
                  </div>
                  <span className={cn(
                    "px-2 py-1 rounded-md text-[10px] font-bold uppercase",
                    report.status === 'searching' ? "bg-brand-warning/10 text-brand-warning" : "bg-brand-success/10 text-brand-success"
                  )}>
                    {report.status}
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-1 mb-3">{report.description}</p>
                <div className="flex items-center text-brand-primary text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                  <MessageSquare className="w-3 h-3 mr-1" />
                  Chat with Conductor
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Chat Modal for Lost Items */}
      <AnimatePresence>
        {activeChatReport && (
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed inset-0 z-50 bg-white flex flex-col max-w-md mx-auto"
          >
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center">
                <button onClick={() => setActiveChatReport(null)} className="p-2 mr-2">
                  <X className="w-5 h-5 text-slate-400" />
                </button>
                <div>
                  <h4 className="font-bold text-slate-900">Conductor Support</h4>
                  <p className="text-[10px] text-slate-500">Regarding: {activeChatReport.itemName}</p>
                </div>
              </div>
              <div className="w-2 h-2 bg-brand-success rounded-full animate-pulse" />
            </div>

            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={cn(
                  "max-w-[80%] p-4 rounded-2xl text-sm",
                  msg.sender === 'user' 
                    ? "bg-brand-primary text-white ml-auto rounded-tr-none" 
                    : "bg-white text-slate-700 mr-auto rounded-tl-none shadow-sm"
                )}>
                  {msg.text}
                </div>
              ))}
            </div>

            <div className="p-4 border-t border-slate-100 bg-white">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Type your message..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 bg-slate-100 border-none rounded-xl px-4 py-3 text-sm outline-none"
                />
                <button 
                  onClick={handleSendMessage}
                  className="p-3 bg-brand-primary text-white rounded-xl shadow-lg shadow-brand-primary/20"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live Tracking & Chat Modal from History */}
      <AnimatePresence>
        {trackingBus && (
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed inset-0 z-50 bg-white flex flex-col max-w-md mx-auto"
          >
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center">
                <button onClick={() => setTrackingBus(null)} className="p-2 mr-2">
                  <X className="w-5 h-5 text-slate-400" />
                </button>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-900 font-display font-bold mr-3">
                    {trackingBus.routeNumber}
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900">Live Tracking</h4>
                    <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Bus {trackingBus.id} • {trackingBus.destination}</p>
                  </div>
                </div>
              </div>
              <div className="w-2 h-2 bg-brand-success rounded-full animate-pulse" />
            </div>

            {/* Live Map Placeholder */}
            <div className="h-48 bg-slate-100 relative overflow-hidden">
              <div className="absolute inset-0 bg-[url('https://picsum.photos/seed/map/800/400')] bg-cover bg-center opacity-40 grayscale" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <div className="absolute -inset-4 bg-brand-primary/20 rounded-full animate-ping" />
                  <div className="relative bg-brand-primary p-3 rounded-full shadow-xl">
                    <BusIcon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>
              <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-md p-3 rounded-2xl border border-white shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <MapPin className="w-4 h-4 text-brand-primary mr-2" />
                    <span className="text-xs font-bold text-slate-700">Near Central Station</span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Updating Live</span>
                </div>
              </div>
            </div>

            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={cn(
                  "max-w-[80%] p-4 rounded-2xl text-sm",
                  msg.sender === 'user' 
                    ? "bg-brand-primary text-white ml-auto rounded-tr-none" 
                    : "bg-white text-slate-700 mr-auto rounded-tl-none shadow-sm"
                )}>
                  {msg.text}
                </div>
              ))}
            </div>

            <div className="p-4 border-t border-slate-100 bg-white">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Message the conductor..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 bg-slate-100 border-none rounded-xl px-4 py-3 text-sm outline-none"
                />
                <button 
                  onClick={handleSendMessage}
                  className="p-3 bg-brand-primary text-white rounded-xl shadow-lg shadow-brand-primary/20"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Reliable Support Info */}
      <div className="bg-slate-900 p-6 rounded-3xl text-white flex items-start space-x-4">
        <div className="p-3 bg-white/10 rounded-2xl">
          <AlertTriangle className="w-6 h-6 text-brand-warning" />
        </div>
        <div>
          <h4 className="font-bold mb-1">Reliable Support</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Our system is connected directly to the bus terminal. Lost items are logged by conductors at the end of each shift.
          </p>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col max-w-md mx-auto shadow-2xl relative overflow-hidden font-sans">
      {/* Login Screen */}
      {!isAuthenticated ? (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-brand-primary to-blue-600 p-6">
          <div className="w-full max-w-sm">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-white rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <BusIcon className="w-8 h-8 text-brand-primary" />
              </div>
              <h1 className="text-4xl font-display font-bold text-white mb-2">OmniBus</h1>
              <p className="text-blue-100">Smart Transit Tracker</p>
            </div>

            <div className="bg-white rounded-3xl p-8 shadow-2xl space-y-6">
              <div>
                <label className="block text-sm font-bold text-slate-600 mb-2">Email</label>
                <input
                  type="email"
                  placeholder="your@email.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                  className="w-full px-4 py-3 bg-slate-100 border-none rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-primary/20"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-slate-600 mb-2">Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                  className="w-full px-4 py-3 bg-slate-100 border-none rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-primary/20"
                />
              </div>

              <button
                onClick={handleLogin}
                disabled={isLoading}
                className="w-full py-3 bg-brand-primary text-white rounded-xl font-bold hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <>
      {/* Header */}
      <header className="p-6 pb-2 bg-white/80 backdrop-blur-md sticky top-0 z-30">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-display font-bold text-slate-900">OmniBus</h1>
            <p className="text-xs text-slate-500 font-medium">
              {isConductorMode ? 'Conductor Terminal' : 'Smart Transit Tracker'} • {authUser?.name}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setIsConductorMode(!isConductorMode)}
              className={cn(
                "p-2 rounded-xl transition-colors relative",
                isConductorMode ? "bg-brand-primary text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
              title="Toggle Conductor Mode"
            >
              <UserCheck className="w-5 h-5" />
            </button>
            <button className="p-2 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors relative">
              <Bell className="w-5 h-5 text-slate-600" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-brand-danger rounded-full border-2 border-white"></span>
            </button>
            <button
              onClick={handleLogout}
              className="p-2 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5 text-slate-600" />
            </button>
          </div>
        </div>

        {activeTab === 'buses' && (
          <>
            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search route or destination..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-slate-100 border-none rounded-2xl text-sm focus:ring-2 focus:ring-brand-primary/20 transition-all outline-none"
              />
            </div>

            {/* Filters */}
            <div className="flex space-x-2 overflow-x-auto pb-2 no-scrollbar">
              {(['all', 'available', 'partial', 'full'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setActiveFilter(filter)}
                  className={cn(
                    "px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider whitespace-nowrap transition-all",
                    activeFilter === filter
                      ? "bg-slate-900 text-white shadow-lg shadow-slate-200"
                      : "bg-white text-slate-500 border border-slate-200 hover:border-slate-300"
                  )}
                >
                  {filter}
                </button>
              ))}
            </div>
          </>
        )}

        {activeTab === 'history' && (
          <div className="pb-4">
            <h2 className="text-xl font-bold text-slate-900">Travel History</h2>
            <p className="text-xs text-slate-500">Your past journeys and records</p>
          </div>
        )}

        {activeTab === 'safety' && (
          <div className="pb-4">
            <h2 className="text-xl font-bold text-slate-900">Safety & Support</h2>
            <p className="text-xs text-slate-500">Emergency SOS and Lost & Found</p>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 p-6 space-y-6">
        <AnimatePresence mode="wait">
          {activeTab === 'buses' && (
            <motion.div
              key="buses"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              {/* Stats Card */}
              <div className={cn(
                "p-6 rounded-[2rem] text-white relative overflow-hidden shadow-xl transition-colors duration-500",
                isConductorMode ? "bg-slate-900 shadow-slate-900/20" : "bg-brand-primary shadow-brand-primary/20"
              )}>
                <div className="relative z-10">
                  <h2 className="text-lg font-bold mb-1">
                    {isConductorMode ? 'Live Ticket Counter' : 'Welcome back!'}
                  </h2>
                  <p className="text-blue-100 text-sm mb-4">
                    {isConductorMode ? 'Update occupancy as tickets are sold.' : '3 buses arriving at your stop soon.'}
                  </p>
                  <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm p-3 rounded-2xl inline-flex">
                    <Info className="w-4 h-4" />
                    <span className="text-xs font-medium">
                      {isConductorMode ? 'Changes sync instantly to all passengers.' : 'AI predicts low crowd levels today.'}
                    </span>
                  </div>
                </div>
                <div className="absolute -right-8 -bottom-8 opacity-20">
                  <BusIcon className="w-48 h-48" />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">
                  {isConductorMode ? 'Manage Bus Occupancy' : 'Live Buses'}
                </h3>
                <Filter className="w-4 h-4 text-slate-400" />
              </div>

              {/* Bus List */}
              <div className="space-y-4 pb-24">
                <AnimatePresence mode="popLayout">
                  {filteredBuses.length > 0 ? (
                    filteredBuses.map((bus) => (
                      <div key={bus.id} className="relative">
                        <BusCard
                          bus={bus}
                          onClick={(bus) => setSelectedBus(bus)}
                        />
                        {isConductorMode && (
                          <div className="absolute right-4 bottom-4 flex space-x-2 z-20">
                            <button 
                              onClick={(e) => { e.stopPropagation(); handleCancelTicket(bus.id); }}
                              className="p-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 text-brand-danger"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={(e) => { e.stopPropagation(); handleSellTicket(bus.id); }}
                              className="p-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 text-brand-success"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-center py-12"
                    >
                      <div className="bg-slate-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-8 h-8 text-slate-300" />
                      </div>
                      <p className="text-slate-500 font-medium">No buses found matching your search.</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {activeTab === 'history' && renderHistory()}
          {activeTab === 'safety' && renderSafety()}
          
          {activeTab === 'map' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-20 text-center"
            >
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                <MapIcon className="w-10 h-10 text-slate-300" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 capitalize">{activeTab} View</h3>
              <p className="text-sm text-slate-500">This feature is coming soon in the next update.</p>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white/80 backdrop-blur-lg border-t border-slate-100 p-4 flex justify-around items-center z-40">
        <button 
          onClick={() => setActiveTab('buses')}
          className={cn("flex flex-col items-center space-y-1 transition-colors", activeTab === 'buses' ? "text-brand-primary" : "text-slate-400")}
        >
          <BusIcon className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase">Buses</span>
        </button>
        <button 
          onClick={() => setActiveTab('map')}
          className={cn("flex flex-col items-center space-y-1 transition-colors", activeTab === 'map' ? "text-brand-primary" : "text-slate-400")}
        >
          <MapIcon className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase">Map</span>
        </button>
        <button 
          onClick={() => setActiveTab('history')}
          className={cn("flex flex-col items-center space-y-1 transition-colors", activeTab === 'history' ? "text-brand-primary" : "text-slate-400")}
        >
          <History className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase">History</span>
        </button>
        <button 
          onClick={() => setActiveTab('safety')}
          className={cn("flex flex-col items-center space-y-1 transition-colors", activeTab === 'safety' ? "text-brand-primary" : "text-slate-400")}
        >
          <ShieldAlert className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase">Safety</span>
        </button>
      </nav>

      {/* Details Modal */}
      <AnimatePresence>
        {selectedBus && (
          <BusDetails
            bus={selectedBus}
            onClose={() => setSelectedBus(null)}
          />
        )}
      </AnimatePresence>

      {/* Background Decorations */}
      <div className="fixed -top-24 -left-24 w-64 h-64 bg-brand-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed -bottom-24 -right-24 w-64 h-64 bg-brand-warning/5 rounded-full blur-3xl pointer-events-none" />
        </>
      )}
    </div>
  );
}
