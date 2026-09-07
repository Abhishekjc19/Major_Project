package com.buscrowd.app.models;

public class ConductorTicket {

    public String ticketId;
    public String busId;
    public String routeId;
    public String tripId;
    public int    boardingStopSeq;
    public int    destStopSeq;
    public String timestamp;      // ISO-8601
    public int    passengerCount;
    public double fare;
    public int    busCapacity;
    public boolean isSynced;

    public ConductorTicket() {}

    public ConductorTicket(String ticketId, String busId, String routeId, String tripId,
                           int boardingStopSeq, int destStopSeq, String timestamp,
                           int passengerCount, double fare, int busCapacity, boolean isSynced) {
        this.ticketId       = ticketId;
        this.busId          = busId;
        this.routeId        = routeId;
        this.tripId         = tripId;
        this.boardingStopSeq = boardingStopSeq;
        this.destStopSeq    = destStopSeq;
        this.timestamp      = timestamp;
        this.passengerCount = passengerCount;
        this.fare           = fare;
        this.busCapacity    = busCapacity;
        this.isSynced       = isSynced;
    }
}
