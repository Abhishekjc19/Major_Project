-- ============================================
-- OmniBus Supabase Schema Setup
-- Copy and paste this entire script into Supabase SQL Editor
-- ============================================

-- 1. USERS TABLE
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  name VARCHAR NOT NULL,
  role VARCHAR DEFAULT 'passenger' NOT NULL,
  phone VARCHAR NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. BUSES TABLE
CREATE TABLE buses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  route_number VARCHAR UNIQUE NOT NULL,
  destination VARCHAR NOT NULL,
  capacity INTEGER NOT NULL,
  current_occupancy INTEGER DEFAULT 0 NOT NULL,
  status VARCHAR DEFAULT 'available' NOT NULL,
  current_location_lat DECIMAL(10, 8) NULL,
  current_location_lon DECIMAL(11, 8) NULL,
  last_updated VARCHAR DEFAULT 'Just now' NOT NULL,
  assigned_conductor_id UUID NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. BUS_STOPS TABLE
CREATE TABLE bus_stops (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  street_address VARCHAR NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. ROUTE_STOPS TABLE
CREATE TABLE route_stops (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sequence_order INTEGER NOT NULL,
  estimated_arrival_time TIME NULL,
  is_passed BOOLEAN DEFAULT false NOT NULL,
  bus_id UUID NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
  stop_id UUID NOT NULL REFERENCES bus_stops(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. RIDE_HISTORY TABLE
CREATE TABLE ride_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ride_date DATE NOT NULL,
  fare DECIMAL(10, 2) NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  bus_id UUID NULL REFERENCES buses(id) ON DELETE SET NULL,
  from_stop_id UUID NULL REFERENCES bus_stops(id) ON DELETE SET NULL,
  to_stop_id UUID NULL REFERENCES bus_stops(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. LOST_ITEMS TABLE
CREATE TABLE lost_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_name VARCHAR NOT NULL,
  description VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'searching' NOT NULL,
  reported_date DATE NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  bus_id UUID NULL REFERENCES buses(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 7. CHAT_MESSAGES TABLE
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_text TEXT NOT NULL,
  lost_item_id UUID NOT NULL REFERENCES lost_items(id) ON DELETE CASCADE,
  sender_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 8. SOS_ALERTS TABLE
CREATE TABLE sos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status VARCHAR DEFAULT 'active' NOT NULL,
  description TEXT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  bus_id UUID NULL REFERENCES buses(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP NULL
);

-- ============================================
-- Create Indexes for Better Performance
-- ============================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_buses_route_number ON buses(route_number);
CREATE INDEX idx_buses_conductor ON buses(assigned_conductor_id);
CREATE INDEX idx_route_stops_bus ON route_stops(bus_id);
CREATE INDEX idx_ride_history_user ON ride_history(user_id);
CREATE INDEX idx_ride_history_bus ON ride_history(bus_id);
CREATE INDEX idx_lost_items_user ON lost_items(user_id);
CREATE INDEX idx_lost_items_bus ON lost_items(bus_id);
CREATE INDEX idx_chat_messages_item ON chat_messages(lost_item_id);
CREATE INDEX idx_sos_alerts_user ON sos_alerts(user_id);
CREATE INDEX idx_sos_alerts_bus ON sos_alerts(bus_id);

-- ============================================
-- Enable Row Level Security (Optional)
-- ============================================
-- Uncomment if you want to enable RLS for security

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE buses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bus_stops ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE route_stops ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ride_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE lost_items ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sos_alerts ENABLE ROW LEVEL SECURITY;
