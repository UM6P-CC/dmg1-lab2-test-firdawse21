-- RLMS Schema (reconstructed from Lab 1 requirements, Lab 2 answer-key fragments,
-- and the Chen ER diagram). VERIFY markers indicate fields whose exact name
-- I was not 100% certain of from prior sessions.

CREATE DATABASE IF NOT EXISTS RLMS;
USE RLMS;

CREATE TABLE Person (
    PersonID        CHAR(6) PRIMARY KEY,
    FullName        VARCHAR(120) NOT NULL,
    InstitutionalEmail VARCHAR(120) NOT NULL UNIQUE,
    PhoneNumber     VARCHAR(25),
    Affiliation     VARCHAR(120)
);

CREATE TABLE ResearchUser (
    PersonID            CHAR(6) PRIMARY KEY,
    AcademicCategory    VARCHAR(60),
    InstitutionalStatus VARCHAR(60),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
);

-- The company itself: tracked independently of any individual technician.
-- ContactPerson/Phone here represent a generic point of contact for the
-- company (e.g. an account manager), which may differ from whichever
-- specific ExternalTechnician person is dispatched for a given job.
CREATE TABLE ServiceProvider (
    ProviderID        CHAR(6) PRIMARY KEY,
    CompanyName       VARCHAR(120) NOT NULL,
    ContactPerson     VARCHAR(100),
    Phone             VARCHAR(25),
    ContractReference VARCHAR(60)
);

CREATE TABLE TechnicalStaff (
    PersonID      CHAR(6) PRIMARY KEY,
    Role          VARCHAR(60),
    ExpertiseArea VARCHAR(100),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
);

-- ISA under TechnicalStaff: every technician is internal or external (total,
-- disjoint -- a TechnicalStaff row should have exactly one of these two
-- matching child rows). "Hire date" only makes sense for an employee, so it
-- moves here rather than living on the shared TechnicalStaff parent.
CREATE TABLE InternalTechnician (
    PersonID CHAR(6) PRIMARY KEY,
    HireDate DATE,
    FOREIGN KEY (PersonID) REFERENCES TechnicalStaff(PersonID)
);

-- An external technician is still a PERSON (they show up and do the work),
-- but they work on behalf of a company. CompanyName/ContractReference are
-- the technician's own attributes here (which company, under which
-- contract, they are currently associated with); the company itself -- with
-- its own generic point of contact, independent of any one technician -- is
-- tracked separately in ServiceProvider below.
CREATE TABLE ExternalTechnician (
    PersonID          CHAR(6) PRIMARY KEY,
    CompanyName       VARCHAR(120),
    ContractReference VARCHAR(60),
    ProviderID        CHAR(6),
    FOREIGN KEY (PersonID) REFERENCES TechnicalStaff(PersonID),
    FOREIGN KEY (ProviderID) REFERENCES ServiceProvider(ProviderID)
);

CREATE TABLE Laboratory (
    LabID        CHAR(6) PRIMARY KEY,
    Name         VARCHAR(100) NOT NULL,
    Building     VARCHAR(50),
    RoomNumber   VARCHAR(20),
    ResearchArea VARCHAR(100),
    SupervisorID CHAR(6),
    FOREIGN KEY (SupervisorID) REFERENCES ResearchUser(PersonID)
);

CREATE TABLE AttachedTo (
    PersonID CHAR(6),
    LabID    CHAR(6),
    PRIMARY KEY (PersonID, LabID),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID)
);

CREATE TABLE ResearchProject (
    ProjectCode   CHAR(6) PRIMARY KEY,
    Title         VARCHAR(150) NOT NULL,
    StartDate     DATE,
    EndDate       DATE,
    FundingSource VARCHAR(100),
    Status        VARCHAR(30)
);

CREATE TABLE ProjectParticipation (
    PersonID    CHAR(6),
    ProjectCode CHAR(6),
    ProjectRole VARCHAR(50),
    PRIMARY KEY (PersonID, ProjectCode),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode)
);

CREATE TABLE EquipmentModel (
    ModelID                  CHAR(6) PRIMARY KEY,
    CommercialName           VARCHAR(100) NOT NULL,
    Manufacturer             VARCHAR(100),
    Category                 VARCHAR(60),
    RequiredEnvironment      VARCHAR(100),
    SpecialTrainingMandatory BOOLEAN
);

CREATE TABLE EquipmentUnit (
    SerialNumber    CHAR(10) PRIMARY KEY,
    AcquisitionDate DATE,
    PurchaseCost    DECIMAL(10,2),
    CurrentStatus   VARCHAR(30),
    IsPortable      BOOLEAN,
    LabID           CHAR(6),
    ModelID         CHAR(6),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID),
    FOREIGN KEY (ModelID) REFERENCES EquipmentModel(ModelID)
);

CREATE TABLE Certification (
    CertificationCode CHAR(6) PRIMARY KEY,
    Title             VARCHAR(120) NOT NULL,
    IssuingAuthority  VARCHAR(100),
    ValidityPeriod    INT,           -- VERIFY: months, or stored as duration
    SafetyLevel       VARCHAR(30)
);

CREATE TABLE HoldsCertification (
    PersonID          CHAR(6),
    CertificationCode CHAR(6),
    IssueDate         DATE,
    ExpirationDate    DATE,
    ResultOrGrade     VARCHAR(30),
    PRIMARY KEY (PersonID, CertificationCode),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (CertificationCode) REFERENCES Certification(CertificationCode)
);

CREATE TABLE RequiresCertification (
    ModelID           CHAR(6),
    CertificationCode CHAR(6),
    PRIMARY KEY (ModelID, CertificationCode),
    FOREIGN KEY (ModelID) REFERENCES EquipmentModel(ModelID),
    FOREIGN KEY (CertificationCode) REFERENCES Certification(CertificationCode)
);

CREATE TABLE Reservation (
    ReservationID       CHAR(6) PRIMARY KEY,
    SubmissionTimestamp DATETIME,
    PlannedStartTime    DATETIME,
    PlannedEndTime       DATETIME,
    Purpose             VARCHAR(150),
    Status              VARCHAR(20),  -- Pending, Approved, Rejected, Cancelled, Completed
    PersonID            CHAR(6) NOT NULL,
    SerialNumber        CHAR(10) NOT NULL,
    ProjectCode         CHAR(6),       -- optional
    ApprovedBy          CHAR(6),       -- optional
    FOREIGN KEY (PersonID) REFERENCES ResearchUser(PersonID),
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode),
    FOREIGN KEY (ApprovedBy) REFERENCES Person(PersonID)
);

CREATE TABLE UsageSession (
    SessionID       CHAR(6) PRIMARY KEY,
    ActualStartTime DATETIME,
    ActualEndTime   DATETIME,
    Purpose         VARCHAR(150),
    Outcome         VARCHAR(100),
    SerialNumber    CHAR(10) NOT NULL,
    ResearchUserID  CHAR(6) NOT NULL,
    ReservationID   CHAR(6),   -- optional
    ProjectCode     CHAR(6),   -- optional
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (ResearchUserID) REFERENCES ResearchUser(PersonID),
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode)
);

-- VERIFY: Maintenance technician is "exactly one technician, internal or
-- external" per Lab 1 text -> the internal/external distinction now lives
-- in the TechnicalStaff ISA hierarchy (InternalTechnician/ExternalTechnician
-- above) rather than as two separate nullable FKs here, so Maintenance only
-- needs a single FK to TechnicalStaff.
CREATE TABLE Maintenance (
    MaintenanceID    CHAR(6) PRIMARY KEY,
    MaintenanceDate  DATE,
    MaintenanceType  VARCHAR(30),  -- Preventive / Corrective
    Description      VARCHAR(255),
    Cost             DECIMAL(10,2),
    DowntimeDuration INT,          -- VERIFY: unit (hours?)
    Outcome          VARCHAR(100),
    SerialNumber     CHAR(10) NOT NULL,
    TechnicianID     CHAR(6) NOT NULL,  -- FK -> TechnicalStaff(PersonID); resolves
                                         -- to an InternalTechnician or
                                         -- ExternalTechnician row
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (TechnicianID) REFERENCES TechnicalStaff(PersonID)
);

-- Weak entity: identified by (SerialNumber, CalibrationNumber)
CREATE TABLE CalibrationRecord (
    SerialNumber    CHAR(10),
    CalibrationNumber INT,
    CalibrationDate DATE,
    CalibrationType VARCHAR(30),
    Result          VARCHAR(30),
    NextDueDate     DATE,
    Remarks         VARCHAR(255),
    PRIMARY KEY (SerialNumber, CalibrationNumber),
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber)
);

CREATE TABLE Consumable (
    ConsumableID     CHAR(6) PRIMARY KEY,
    Name             VARCHAR(100) NOT NULL,
    UnitOfMeasure    VARCHAR(30),
    HazardLevel      VARCHAR(30),
    ReorderThreshold INT,
    Supplier         VARCHAR(100)
);

CREATE TABLE Stores (
    LabID             CHAR(6),
    ConsumableID      CHAR(6),
    QuantityAvailable INT,
    StorageCondition  VARCHAR(60),
    LastRestockDate   DATE,
    PRIMARY KEY (LabID, ConsumableID),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID),
    FOREIGN KEY (ConsumableID) REFERENCES Consumable(ConsumableID)
);

CREATE TABLE Consumes (
    SessionID    CHAR(6),
    ConsumableID CHAR(6),
    QuantityUsed INT,
    PRIMARY KEY (SessionID, ConsumableID),
    FOREIGN KEY (SessionID) REFERENCES UsageSession(SessionID),
    FOREIGN KEY (ConsumableID) REFERENCES Consumable(ConsumableID)
);