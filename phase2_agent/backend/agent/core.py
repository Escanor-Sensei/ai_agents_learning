"""
Agent Core — agent/core.py
Responsible for building the ReAct agent graph.

.NET analogy:
  This file = builder.Services.AddScoped<IAgentService, AgentService>()
  build_agent() = the factory method that wires LLM + tools + memory together
  Nothing here knows about CLI, sessions, or user input — pure construction.
"""

import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import all_tools
from memory import create_memory

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

_SYSTEM_PROMPT = """You are a helpful assistant. Use tools when needed. Be concise.

When writing SQL queries, use ONLY these tables and columns:

- Flights(Id, FlightNumber, DepartureTime, ArrivalTime, AircraftType, Status, CreatedAt, UpdatedAt)
- Passengers(Id, PassengerName, Email, BookingReference, CreatedAt, UpdatedAt)
- Seats(Id, FlightId, SeatNumber, SeatClass, Status, CreatedAt, UpdatedAt, RowVersion)
- SeatHold(Id, SeatId, PassengerId, CreatedAt, ExpiresAt, Status, UpdatedAt, RowVersion)
- CheckInSessions(Id, PassengerId, FlightId, Status, CreatedAt, CompletedAt, UpdatedAt, RowVersion, BaggageWeight, BookingReference, CancellationReason, CancelledAt, PassengerEmail)
- BoardingPasses(Id, CheckInSessionId, PassengerEmail, SeatNumber, FlightId, BoardingPassCode, IssuedAt, ExpiresAt, IsUsed, UsedAt)
- Customers(Id, Email, FirstName, LastName, PhoneNumber, CreatedDate, LastLoginDate, IsActive, DateOfBirth, LastModifiedDate, LoyaltyPoints)
- Products(Id, Sku, Name, Description, Price, Category, IsActive, CreatedDate, LastModifiedDate)
- Orders(Id, OrderNumber, CustomerId, OrderDate, Status, TotalAmount, ShippingCost, TaxAmount, ShippingAddressId, BillingAddressId, ShippedDate, DeliveredDate, TrackingNumber)
- OrderItems(Id, OrderId, ProductId, ProductName, Quantity, UnitPrice, Discount, TotalPrice)
- Payments(Id, OrderId, PaymentMethod, Amount, Status, TransactionId, PaymentGateway, PaymentDate, ProcessedDate, CreatedDate, Currency, RefundedDate, CardLastFourDigits, CardType)
- PaymentTransactions(Id, PaymentId, Action, OldStatus, NewStatus, ErrorMessage, TransactionDate, GatewayResponse, TransactionType, Amount, Status, ProcessorTransactionId, ResponseMessage, ErrorCode)
- Inventories(Id, ProductId, QuantityOnHand, QuantityReserved, ReorderLevel, ReorderQuantity, ReorderPoint, WarehouseLocation, LastStockUpdateDate, LastUpdated, RowVersion)
- InventoryTransactions(Id, ProductId, QuantityChange, Quantity, TransactionType, Type, Reason, ReferenceNumber, TransactionDate, PerformedBy)
- Notifications(Id, CustomerId, Type, Recipient, Subject, Message, Title, Status, CreatedDate, SentDate, RetryCount, ErrorMessage, TemplateId, TemplateData, Channel, Priority, ScheduledDate, IsRead, ReadDate)
- NotificationTemplates(Id, TemplateCode, Type, Subject, Body, IsActive, CreatedDate, LastModifiedDate)
- CustomerAddresses(Id, CustomerId, Street, City, State, ZipCode, Country, IsDefault, AddressType, CreatedDate, LastModifiedDate, IsActive)
- BaggageRequests(Id, CheckInSessionId, Weight, ExcessFee, Status, CreatedAt, UpdatedAt, RowVersion)

Do NOT invent column names. Use only the columns listed above.
"""


def build_agent():
    """
    Constructs and returns the ReAct agent with tools and memory wired in.

    .NET analogy:
      Like a factory method returning a fully configured IAgentService.
      Caller doesn't need to know how LLM, tools, or memory are assembled.
    """
    llm = ChatOllama(model=MODEL)
    memory = create_memory()

    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        checkpointer=memory,
        prompt=_SYSTEM_PROMPT,
    )

    return agent, all_tools, MODEL
