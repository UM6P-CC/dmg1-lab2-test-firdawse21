-- ============================================================
-- LAB 5 SEED DATASET (Views, Triggers)
-- ============================================================
-- Independent dataset, dedicated to Lab 5, with its own ID namespace
-- (W-prefixed people, V-prefixed labs, U-prefixed models, WN-prefixed
-- units, WR-prefixed reservations, WP-prefixed projects, WT-prefixed
-- technicians/maintenance). Like Lab 4, several views are date-relative
-- (CURDATE()-anchored), so reservation dates here are expressed as
-- CURDATE() +/- INTERVAL n DAY rather than fixed calendar dates.
--
-- This seed is designed so that:
--   - View 1 (UpcomingReservationsByLab) has a genuine multi-day,
--     multi-lab answer within the next 14 days, AND a reservation just
--     outside that window (the exclusion trap).
--   - View 2 (EquipmentUsageSummary) has units in every state
--     (Operational, UnderMaintenance) across multiple labs/models, plus
--     a currently-active Approved reservation overlapping NOW() so
--     ReservedUnits is non-trivially non-zero for at least one row.
--   - View 3 (ResearchUserReservationThirty) has a user with a mix of
--     Approved/Pending/Cancelled in the last 30 days, AND a user with
--     ZERO reservations in that window (the "treat missing as zero" case).
--   - View 4 (ProjectNextReservation) has a project with several future
--     Approved reservations (so MIN() matters, not just "the only one"),
--     and a project with NO Approved future reservation (must not
--     appear in the view at all).

-- ============================================================
-- PEOPLE
-- ============================================================
INSERT INTO Person (PersonID, FullName, InstitutionalEmail, PhoneNumber, Affiliation) VALUES
('W00001', 'Salim Touimi',   'salim.touimi@um6p.ma',   '0651111111', 'UM6P'),
('W00002', 'Houda Lamrani',  'houda.lamrani@um6p.ma',  '0652222222', 'UM6P'),
('W00003', 'Younes Berrada', 'younes.berrada@um6p.ma', '0653333333', 'UM6P'),
('W00004', 'Amal Sefiani',   'amal.sefiani@um6p.ma',   '0654444444', 'UM6P'),
('W00005', 'Tariq Idrissi',  'tariq.idrissi@um6p.ma',  '0655555555', 'UM6P'),
('W00006', 'Nora Chafik',    'nora.chafik@um6p.ma',    '0656666666', 'UM6P'),
('W00007', 'Bilal Ouazzani', 'bilal.ouazzani@um6p.ma', '0657777777', 'UM6P'),
('W00008', 'Ghita Naciri',   'ghita.naciri@um6p.ma',   '0658888888', 'UM6P'),
('W00009', 'Aymane Fassi',   'aymane.fassi@um6p.ma',   '0659999999', 'UM6P');

INSERT INTO ResearchUser (PersonID, AcademicCategory, InstitutionalStatus) VALUES
('W00001', 'Faculty', 'Active'),
('W00002', 'PhD',     'Active'),
('W00003', 'PostDoc', 'Active'),
('W00004', 'Faculty', 'Active'),
('W00005', 'Master',  'Active'),
('W00006', 'PhD',     'Active'),
('W00007', 'Faculty', 'Active'),
('W00008', 'PhD',     'Active');

-- W00009 is the dedicated technician used by the Maintenance trigger tests
-- (kept out of ResearchUser; this person is purely TechnicalStaff).
INSERT INTO TechnicalStaff (PersonID, Role, ExpertiseArea) VALUES
('W00009', 'Lab Technician', 'General Maintenance');
INSERT INTO InternalTechnician (PersonID, HireDate) VALUES
('W00009', '2022-01-10');

-- ============================================================
-- LABORATORIES
-- ============================================================
INSERT INTO Laboratory (LabID, Name, Building, RoomNumber, ResearchArea, SupervisorID) VALUES
('V0001', 'PhotonicsLab', 'East Tower', 'E101', 'Photonics',    'W00001'),
('V0002', 'GenomicsLab',  'East Tower', 'E102', 'Genomics',     'W00004'),
('V0003', 'MaterialsLab', 'West Tower', 'W201', 'Materials',    'W00007'),
-- V0004 is deliberately empty (no EquipmentUnit, no Reservation) so the
-- laboratory-delete trigger test has a genuinely deletable lab to confirm
-- the trigger doesn't block deletion when there's nothing dependent.
('V0004', 'EmptyLab',     'West Tower', 'W202', 'Unassigned',   NULL);

-- ============================================================
-- EQUIPMENT
-- ============================================================
INSERT INTO EquipmentModel (ModelID, CommercialName, Manufacturer, Category, RequiredEnvironment, SpecialTrainingMandatory) VALUES
('U0001', 'PhotonScope P1', 'Zeiss',  'Microscope',  'Clean room', TRUE),
('U0002', 'GeneSeq G2',     'Illumina','Sequencer',  'Standard',   FALSE);

INSERT INTO EquipmentUnit (SerialNumber, AcquisitionDate, PurchaseCost, CurrentStatus, IsPortable, LabID, ModelID) VALUES
('WN00001', '2023-02-01', 30000.00, 'Operational',     FALSE, 'V0001', 'U0001'),
('WN00002', '2023-03-01', 31000.00, 'Operational',     FALSE, 'V0001', 'U0001'),
('WN00003', '2023-04-01', 15000.00, 'UnderMaintenance', TRUE,  'V0002', 'U0002'),
('WN00004', '2023-05-01', 16000.00, 'Operational',     TRUE,  'V0002', 'U0002'),
('WN00005', '2022-01-01', 12000.00, 'Operational',     FALSE, 'V0003', 'U0002');

-- ============================================================
-- RESEARCH PROJECTS
-- WP0001 has multiple future Approved reservations (Q4 view's MIN matters)
-- WP0002 has a future reservation but it's NOT Approved (excluded entirely)
-- ============================================================
INSERT INTO ResearchProject (ProjectCode, Title, StartDate, EndDate, FundingSource, Status) VALUES
('WP0001', 'Photonic Imaging Study', '2026-01-01', '2026-12-31', 'Internal', 'Active'),
('WP0002', 'Genome Mapping',         '2026-01-01', '2026-12-31', 'Ministry', 'Active');

-- ============================================================
-- RESERVATIONS
-- ============================================================
INSERT INTO Reservation (ReservationID, SubmissionTimestamp, PlannedStartTime, PlannedEndTime, Purpose, Status, PersonID, SerialNumber, ProjectCode, ApprovedBy) VALUES
-- --- View 1 target: Approved reservations within the next 14 days ---
('WR0001', NOW(), CURDATE() + INTERVAL 3 DAY,  CURDATE() + INTERVAL 3 DAY + INTERVAL 2 HOUR, 'Imaging', 'Approved', 'W00001', 'WN00001', 'WP0001', 'W00004'),
('WR0002', NOW(), CURDATE() + INTERVAL 3 DAY,  CURDATE() + INTERVAL 3 DAY + INTERVAL 2 HOUR, 'Imaging', 'Approved', 'W00002', 'WN00002', NULL,     'W00004'),
('WR0003', NOW(), CURDATE() + INTERVAL 10 DAY, CURDATE() + INTERVAL 10 DAY + INTERVAL 2 HOUR,'Sequencing','Approved','W00003','WN00004', 'WP0002', 'W00004'),
-- just OUTSIDE the 14-day window (day 16) -- must NOT appear in View 1
('WR0004', NOW(), CURDATE() + INTERVAL 16 DAY, CURDATE() + INTERVAL 16 DAY + INTERVAL 2 HOUR,'Imaging', 'Approved', 'W00001', 'WN00001', NULL, 'W00004'),

-- --- View 2 target: a reservation overlapping the CURRENT moment, so
-- ReservedUnits is non-zero for WN00005 ---
('WR0005', NOW(), NOW() - INTERVAL 1 HOUR, NOW() + INTERVAL 1 HOUR, 'Sequencing', 'Approved', 'W00006', 'WN00005', NULL, 'W00004'),

-- --- View 3 target: last-30-days mix of Approved/Pending/Cancelled ---
-- W00005: 2 Approved, 1 Pending, 1 Cancelled in the last 30 days
('WR0006', NOW(), CURDATE() - INTERVAL 5 DAY,  CURDATE() - INTERVAL 5 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved',  'W00005', 'WN00002', NULL, 'W00004'),
('WR0007', NOW(), CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 10 DAY + INTERVAL 1 HOUR,'Routine', 'Approved',  'W00005', 'WN00004', NULL, 'W00004'),
('WR0008', NOW(), CURDATE() - INTERVAL 15 DAY, CURDATE() - INTERVAL 15 DAY + INTERVAL 1 HOUR,'Routine', 'Pending',   'W00005', 'WN00005', NULL, NULL),
('WR0009', NOW(), CURDATE() - INTERVAL 20 DAY, CURDATE() - INTERVAL 20 DAY + INTERVAL 1 HOUR,'Routine', 'Cancelled', 'W00005', 'WN00002', NULL, NULL),
-- a reservation OUTSIDE the 30-day window for W00005 -- must NOT count
('WR0010', NOW(), CURDATE() - INTERVAL 40 DAY, CURDATE() - INTERVAL 40 DAY + INTERVAL 1 HOUR,'Routine', 'Approved',  'W00005', 'WN00002', NULL, 'W00004'),
-- W00007 has ZERO reservations at all in the last 30 days (the "missing
-- counts as zero" case -- W00007 must still appear in View 3 with all
-- counts at 0, since it's a LEFT JOIN from ResearchUser)

-- --- View 4 target: WP0001 has TWO future Approved reservations
-- (WR00001 in 3 days, WR00011 in 8 days) -- MIN must correctly pick the
-- earlier one (WR00001, day 3), not just "whichever row" ---
('WR0011', NOW(), CURDATE() + INTERVAL 8 DAY, CURDATE() + INTERVAL 8 DAY + INTERVAL 2 HOUR, 'Imaging', 'Approved', 'W00002', 'WN00002', 'WP0001', 'W00004'),
-- WP0002's only future reservation (WR00003 above) is correctly Approved,
-- so WP0002 DOES appear in View 4 -- but let's also prove the "not
-- Approved is excluded" rule with a Pending one closer in time:
('WR0012', NOW(), CURDATE() + INTERVAL 4 DAY, CURDATE() + INTERVAL 4 DAY + INTERVAL 2 HOUR, 'Sequencing', 'Pending', 'W00003', 'WN00004', 'WP0002', NULL);

-- ============================================================
-- MAINTENANCE (for trigger testing; WN00003 already UnderMaintenance above
-- represents a maintenance job already in progress with no Outcome yet)
-- ============================================================
INSERT INTO Maintenance (MaintenanceID, MaintenanceDate, MaintenanceType, Description, Cost, DowntimeDuration, Outcome, SerialNumber, TechnicianID) VALUES
('WT0001', CURDATE() - INTERVAL 2 DAY, 'Corrective', 'Sensor recalibration', 200.00, 4, NULL, 'WN00003', 'W00009');
