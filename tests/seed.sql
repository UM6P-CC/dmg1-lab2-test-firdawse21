USE RLMS;

-- ============================================================
-- PEOPLE
-- ============================================================
INSERT INTO Person (PersonID, FullName, InstitutionalEmail, PhoneNumber, Affiliation) VALUES
('P00001', 'Sara El Amrani',   'sara.elamrani@um6p.ma',   '0611111111', 'UM6P'),
('P00002', 'Yassine Bouzid',   'yassine.bouzid@um6p.ma',  '0622222222', 'UM6P'),
('P00003', 'Imane Tahiri',     'imane.tahiri@um6p.ma',    '0633333333', 'UM6P'),
('P00004', 'Omar Tazi',        'omar.tazi@um6p.ma',       '0644444444', 'UM6P'),
('P00005', 'Khadija Naciri',   'khadija.naciri@um6p.ma',  '0655555555', 'UM6P'),
('P00006', 'Hamza Idrissi',    'hamza.idrissi@um6p.ma',   '0666666666', 'UM6P'),
('P00007', 'Mehdi Alaoui',     'mehdi.alaoui@um6p.ma',    '0677777777', 'UM6P'),
('P00008', 'Salma Bennani',    'salma.bennani@um6p.ma',   '0688888888', 'UM6P'),
('P00009', 'Anas Fassi',       'anas.fassi@um6p.ma',      '0699999999', 'UM6P'),
('P00010', 'Laila Ouahbi',     'laila.ouahbi@um6p.ma',    '0610101010', 'UM6P'),
('P00011', 'Reda Chraibi',     'reda.chraibi@um6p.ma',    '0620202020', 'UM6P');

-- ResearchUsers: P00001..P00009 (P00010, P00011 are TechnicalStaff)
INSERT INTO ResearchUser (PersonID, AcademicCategory, InstitutionalStatus) VALUES
('P00001', 'Faculty',  'Active'),
('P00002', 'PhD',      'Active'),
('P00003', 'PostDoc',  'Active'),
('P00004', 'Faculty',  'Active'),
('P00005', 'Master',   'Active'),
('P00006', 'PhD',      'Active'),
('P00007', 'PhD',      'Active'),
('P00008', 'Master',   'Active'),
('P00009', 'Faculty',  'Active');

INSERT INTO TechnicalStaff (PersonID, Role, ExpertiseArea) VALUES
('P00010', 'Lab Technician', 'Electronics'),
('P00011', 'Lab Technician', 'Chemistry');


INSERT INTO InternalTechnician (PersonID, HireDate) VALUES
('P00010', '2020-01-15'),
('P00011', '2019-06-01');

-- ============================================================
-- LABORATORIES
-- ============================================================

INSERT INTO Laboratory (LabID, Name, Building, RoomNumber, ResearchArea, SupervisorID) VALUES
('L0001', 'ChemLab-1',   'North Wing',         'R101', 'Chemistry',          'P00001'),
('L0002', 'PhysLab-1',   'West Wing',          'R102', 'Physics',            'P00004'),
('L0003', 'AI-Lab',      'Research Center A',  'R201', 'Computer Science',   'P00009'),
('L0004', 'BioLab-A',    'Research Center A',  'R202', 'Biology',            'P00009'),
('L0005', 'ChemLab-2',   'North Wing',         'R103', 'Chemistry',          'P00001');

-- AttachedTo: who can access which lab (independent of supervision)
INSERT INTO AttachedTo (PersonID, LabID) VALUES
('P00001','L0001'), ('P00002','L0001'), ('P00002','L0002'),
('P00003','L0002'), ('P00004','L0002'), ('P00005','L0003'),
('P00007','L0004'), ('P00008','L0004'),
('P00009','L0004'), ('P00010','L0001'), ('P00011','L0004');

-- ============================================================
-- RESEARCH PROJECTS
-- ============================================================
INSERT INTO ResearchProject (ProjectCode, Title, StartDate, EndDate, FundingSource, Status) VALUES
('PR0001', 'Catalysis Study',        '2025-01-01','2025-12-31','Internal',  'Completed'),
('PR0002', 'Quantum Sensors',        '2026-01-01','2026-12-31','Ministry',  'Active'),
('PR0003', 'AI for Genomics',        '2026-02-01','2026-11-30','Internal',  'Active'),
('PR0004', 'Microscopy Methods',     '2026-03-01', NULL,       'Industry',  'Active');

INSERT INTO ProjectParticipation (PersonID, ProjectCode, ProjectRole) VALUES
('P00001','PR0001','PI'),
('P00002','PR0001','Student Assistant'),
('P00004','PR0002','PI'),
('P00002','PR0002','Researcher'),
('P00003','PR0002','Researcher'),
('P00004','PR0003','Co-PI'),
('P00004','PR0004','PI'),
('P00005','PR0003','Student Assistant'),
('P00009','PR0003','PI'),
('P00009','PR0004','Researcher');


-- ============================================================
-- EQUIPMENT
-- ============================================================
INSERT INTO EquipmentModel (ModelID, CommercialName, Manufacturer, Category, RequiredEnvironment, SpecialTrainingMandatory) VALUES
('M0001', 'Axiolab 5',        'Zeiss',     'Microscope',  'Clean room', TRUE),
('M0002', 'Sorvall ST8',      'Thermo',    'Centrifuge',  'Standard',   FALSE),
('M0003', 'NanoDrop One',     'Thermo',    'Spectrometer','Standard',   FALSE),
('M0004', 'EVO 18',           'Zeiss',     'Microscope',  'Clean room', TRUE);


INSERT INTO EquipmentUnit (SerialNumber, AcquisitionDate, PurchaseCost, CurrentStatus, IsPortable, LabID, ModelID) VALUES
('SN000001', '2023-05-10', 45000.00, 'Operational', FALSE, 'L0001', 'M0001'),  -- Microscope in L0001
('SN000002', '2023-06-10', 12000.00, 'Operational', TRUE,  'L0001', 'M0002'),  -- Centrifuge in L0001
('SN000003', '2024-01-15', 30000.00, 'Operational', FALSE, 'L0002', 'M0003'),  -- Spectrometer in L0002
('SN000004', '2022-09-20', 11000.00, 'Operational', TRUE,  'L0003', 'M0002'),  -- Centrifuge in L0003 only
('SN000005', '2024-03-01', 48000.00, 'Operational', FALSE, 'L0004', 'M0004'),  -- Microscope in L0004
('SN000006', '2021-07-07', 10000.00, 'Retired',     TRUE,  'L0002', 'M0002');  -- Centrifuge in L0002 (retired, still counts as equipment)


-- ============================================================
-- CERTIFICATIONS
-- ============================================================
INSERT INTO Certification (CertificationCode, Title, IssuingAuthority, ValidityPeriod, SafetyLevel) VALUES
('C0001', 'Microscopy Safety',  'UM6P Safety Office', 24, 'High'),
('C0002', 'Centrifuge Handling','UM6P Safety Office', 12, 'Medium');

INSERT INTO RequiresCertification (ModelID, CertificationCode) VALUES
('M0001','C0001'), ('M0004','C0001'), ('M0002','C0002');

INSERT INTO HoldsCertification (PersonID, CertificationCode, IssueDate, ExpirationDate, ResultOrGrade) VALUES
('P00001','C0001','2024-01-10','2026-01-10','Pass'),
('P00002','C0002','2024-02-10','2025-02-10','Pass'),
('P00007','C0001','2025-01-10','2027-01-10','Pass'),
('P00008','C0001','2025-01-10','2027-01-10','Pass');

-- ============================================================
-- RESERVATIONS
-- ============================================================
INSERT INTO Reservation (ReservationID, SubmissionTimestamp, PlannedStartTime, PlannedEndTime, Purpose, Status, PersonID, SerialNumber, ProjectCode, ApprovedBy) VALUES
('R0001', '2026-09-02 09:00:00', '2026-09-03 09:00:00', '2026-09-03 12:00:00', 'Imaging session', 'Approved', 'P00007', 'SN000005', 'PR0004', 'P00009'),
('R0002', '2026-09-15 09:00:00', '2026-09-16 09:00:00', '2026-09-16 12:00:00', 'Imaging session', 'Approved', 'P00008', 'SN000005', NULL,     'P00009'),
('R0003', '2026-09-20 09:00:00', '2026-09-21 09:00:00', '2026-09-21 12:00:00', 'Centrifuge run', 'Approved', 'P00002', 'SN000002', NULL, 'P00001'),
('R0004', '2026-08-30 09:00:00', '2026-10-05 09:00:00', '2026-10-05 12:00:00', 'Imaging session', 'Pending',  'P00009', 'SN000005', NULL, NULL),
('R0005', '2026-11-01 10:00:00', '2026-11-06 09:00:00', '2026-11-06 11:00:00', 'Routine use', 'Approved', 'P00001', 'SN000001', NULL, 'P00001'),
('R0006', '2026-11-01 10:00:00', '2026-11-06 13:00:00', '2026-11-06 15:00:00', 'Routine use', 'Approved', 'P00002', 'SN000003', NULL, 'P00004'),
('R0007', '2026-02-01 08:00:00', '2026-02-02 09:00:00', '2026-02-02 11:00:00', 'Spectrometry', 'Approved', 'P00003', 'SN000003', NULL, 'P00001'),
('R0008', '2026-02-05 08:00:00', '2026-02-06 09:00:00', '2026-02-06 11:00:00', 'Spectrometry', 'Approved', 'P00002', 'SN000003', NULL, 'P00004'),
('R0009', '2026-03-01 08:00:00', '2026-03-02 09:00:00', '2026-03-02 11:00:00', 'Routine', 'Approved', 'P00002', 'SN000001', NULL, 'P00001'),
('R0010', '2026-04-01 08:00:00', '2026-04-02 09:00:00', '2026-04-02 11:00:00', 'Routine', 'Completed', 'P00001', 'SN000002', NULL, NULL),
('R0011', '2026-04-05 08:00:00', '2026-04-06 09:00:00', '2026-04-06 11:00:00', 'Routine', 'Completed', 'P00001', 'SN000004', NULL, NULL),
('R0012', '2025-02-01 08:00:00', '2025-02-02 09:00:00', '2025-02-02 11:00:00', 'Routine', 'Completed', 'P00006', 'SN000004', NULL, NULL),
('R0013', '2025-05-01 08:00:00', '2025-05-02 09:00:00', '2025-05-02 11:00:00', 'Routine', 'Completed', 'P00006', 'SN000004', NULL, NULL),
('R0014', '2025-09-01 08:00:00', '2025-09-02 09:00:00', '2025-09-02 11:00:00', 'Routine', 'Completed', 'P00006', 'SN000004', NULL, NULL),
('R0015', '2025-03-01 08:00:00', '2025-03-02 09:00:00', '2025-03-02 11:00:00', 'Routine', 'Completed', 'P00005', 'SN000004', NULL, NULL),
('R0016', '2025-06-01 08:00:00', '2025-06-02 09:00:00', '2025-06-02 11:00:00', 'Routine', 'Completed', 'P00005', 'SN000004', NULL, NULL),
('R0017', '2026-12-01 08:00:00', '2026-12-02 09:00:00', '2026-12-02 11:00:00', 'Imaging session', 'Approved', 'P00007', 'SN000005', NULL, 'P00009'),
('R0018', '2026-12-05 08:00:00', '2026-12-06 09:00:00', '2026-12-06 11:00:00', 'Routine', 'Approved', 'P00006', 'SN000004', NULL, 'P00001'),
('R0019', '2026-12-06 08:00:00', '2026-12-07 09:00:00', '2026-12-07 11:00:00', 'Routine', 'Approved', 'P00006', 'SN000004', NULL, 'P00001'),
('R0020', '2026-12-08 08:00:00', '2026-12-09 09:00:00', '2026-12-09 11:00:00', 'Routine', 'Approved', 'P00005', 'SN000004', NULL, 'P00001');

-- ============================================================
-- USAGE SESSIONS 
-- ============================================================
INSERT INTO UsageSession (SessionID, ActualStartTime, ActualEndTime, Purpose, Outcome, SerialNumber, ResearchUserID, ReservationID, ProjectCode) VALUES
('US0001', '2026-09-03 09:05:00', '2026-09-03 11:50:00', 'Imaging session', 'Success', 'SN000005', 'P00007', 'R0001', 'PR0004'),
('US0002', '2026-09-16 09:10:00', '2026-09-16 11:40:00', 'Imaging session', 'Success', 'SN000005', 'P00008', 'R0002', NULL),
('US0003', '2026-11-06 09:05:00', '2026-11-06 10:50:00', 'Routine use',     'Success', 'SN000001', 'P00001', 'R0005', NULL);