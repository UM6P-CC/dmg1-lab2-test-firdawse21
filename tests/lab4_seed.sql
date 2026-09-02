-- ============================================================
-- LAB 4 SEED DATASET
-- ============================================================
-- A self-contained dataset, independent from Lab 3's seed.sql/seed_shadow.sql.
-- Unlike Lab 3, several Lab 4 queries are deliberately date-RELATIVE
-- (e.g. "next 7 days", "last 90 days"), per instructor's explicit choice
-- to use CURDATE() rather than a fixed reference date. Every date value
-- below is therefore expressed as CURDATE() +/- INTERVAL n DAY, so the
-- expected answers remain correct no matter which day grading runs.
--
-- IDs use a Q4-specific prefix (Z-prefix for people, K-prefix for labs,
-- etc.) to avoid any accidental collision if this is ever loaded into
-- the same database as Lab 3's data; in practice this seed has its own
-- dedicated RLMS_LAB4 database, so collision isn't actually possible, but
-- the distinct prefix also makes it obvious which lab a given ID belongs
-- to when reading raw query output during grading or QA.

-- ============================================================
-- PEOPLE
-- ============================================================
INSERT INTO Person (PersonID, FullName, InstitutionalEmail, PhoneNumber, Affiliation) VALUES
('Z00001', 'Zineb Amrani',   'zineb.amrani@um6p.ma',   '0641111111', 'UM6P'),
('Z00002', 'Walid Bensaid',  'walid.bensaid@um6p.ma',  '0642222222', 'UM6P'),
('Z00003', 'Yasmine Cherif', 'yasmine.cherif@um6p.ma', '0643333333', 'UM6P'),
('Z00004', 'Xavier Driss',   'xavier.driss@um6p.ma',   '0644444444', 'UM6P'),
('Z00005', 'Soraya Essadi',  'soraya.essadi@um6p.ma',  '0645555555', 'UM6P'),
('Z00006', 'Rachid Filali',  'rachid.filali@um6p.ma',  '0646666666', 'UM6P'),
('Z00007', 'Nadia Ghazi',    'nadia.ghazi@um6p.ma',    '0647777777', 'UM6P'),
('Z00008', 'Marouane Haddi', 'marouane.haddi@um6p.ma', '0648888888', 'UM6P');

INSERT INTO ResearchUser (PersonID, AcademicCategory, InstitutionalStatus) VALUES
('Z00001', 'Faculty', 'Active'),
('Z00002', 'PhD',     'Active'),
('Z00003', 'PostDoc', 'Active'),
('Z00004', 'Faculty', 'Active'),
('Z00005', 'Master',  'Active'),
('Z00006', 'PhD',     'Active'),
('Z00007', 'Faculty', 'Active'),
('Z00008', 'PhD',     'Active');

-- ============================================================
-- LABORATORIES
-- Q14 needs at least one lab with EVERY equipment category present, and
-- at least one lab missing some category (the trap). Q18/Q19 group by
-- Building, so we need >= 2 labs sharing a building.
-- ============================================================
INSERT INTO Laboratory (LabID, Name, Building, RoomNumber, ResearchArea, SupervisorID) VALUES
('K0001', 'NanoLab',     'Tower A', 'T101', 'Nanotechnology', 'Z00001'),
('K0002', 'OpticsLab',   'Tower A', 'T102', 'Optics',         'Z00004'),
('K0003', 'RoboticsLab', 'Tower B', 'T201', 'Robotics',       'Z00007'),
('K0004', 'FullStockLab','Tower B', 'T202', 'Materials',      'Z00007'),
-- K0005 exists ONLY to host the Q20 data-quality-violation unit below, in
-- its own building ("Annex C") so it never joins any other query's
-- carefully-tuned Building/Category groupings (Q6, Q9, Q15, Q18, Q19).
('K0005', 'QuarantineLab','Annex C', 'C001', 'Misc',           NULL);

-- ============================================================
-- LAB ATTACHMENTS (needed for Q12: "percentage share of reservations in
-- THEIR laboratory", where "their laboratory" = the lab(s) the person is
-- AttachedTo, per the instructor's chosen interpretation -- not the lab of
-- whichever equipment they happened to reserve).
-- ============================================================
INSERT INTO AttachedTo (PersonID, LabID) VALUES
('Z00001', 'K0001'),
('Z00002', 'K0001'),
('Z00003', 'K0001'),
('Z00004', 'K0002'),
('Z00005', 'K0002'),
('Z00006', 'K0003'),
('Z00007', 'K0004'),
('Z00008', 'K0004');

-- ============================================================
-- EQUIPMENT MODELS (4 categories used across the lab)
-- ============================================================
INSERT INTO EquipmentModel (ModelID, CommercialName, Manufacturer, Category, RequiredEnvironment, SpecialTrainingMandatory) VALUES
('N0001', 'NanoScope X',     'Zeiss',   'Microscope',   'Clean room', TRUE),
('N0002', 'SpinPro 9',       'Thermo',  'Centrifuge',   'Standard',   FALSE),
('N0003', 'SpectraMax',      'Agilent', 'Spectrometer', 'Standard',   FALSE),
('N0004', 'ThermoCycler T1', 'Bio-Rad', 'Thermocycler', 'Standard',   FALSE);

-- ============================================================
-- EQUIPMENT UNITS
-- Q7: "labs with > 10 units" -- deliberately NONE qualify (seed keeps
--     counts small/realistic); confirms a correct query returns empty,
--     not a fabricated lab.
-- Q14: K0004 ("FullStockLab") has all 4 categories -- the unique answer.
--      K0001/K0002/K0003 each miss at least one category.
-- Q19: Tower A's Microscope units span a wide cost range (qualifies);
--      Tower B's units are kept close in cost (does not qualify) --
--      gives Q19 a real, discriminating answer.
-- Q13: two units marked 'UnderMaintenance'.
-- ============================================================
INSERT INTO EquipmentUnit (SerialNumber, AcquisitionDate, PurchaseCost, CurrentStatus, IsPortable, LabID, ModelID) VALUES
-- K0001 (NanoLab, Tower A): Microscope + Centrifuge, wide microscope cost spread
('ZN000001', '2023-01-10', 20000.00, 'Operational',      FALSE, 'K0001', 'N0001'),
('ZN000002', '2023-02-15', 32000.00, 'Operational',      FALSE, 'K0001', 'N0001'),  -- wide spread vs ZN000001
('ZN000003', '2023-03-01', 9000.00,  'UnderMaintenance',  TRUE,  'K0001', 'N0002'),

-- K0002 (OpticsLab, Tower A): Spectrometer only, plus a Microscope unit
-- (keeps Tower A's Microscope spread wide across labs in this building)
('ZN000004', '2023-04-05', 27000.00, 'Operational',      FALSE, 'K0002', 'N0003'),
('ZN000005', '2023-05-12', 21000.00, 'Operational',      FALSE, 'K0002', 'N0001'),

-- K0003 (RoboticsLab, Tower B): Centrifuge + Thermocycler, costs close together
('ZN000006', '2022-09-20', 10000.00, 'Operational',      TRUE,  'K0003', 'N0002'),
('ZN000007', '2022-10-01', 10800.00, 'UnderMaintenance',  FALSE, 'K0003', 'N0004'),

-- K0004 (FullStockLab, Tower B): one of EVERY category -- the Q14 answer.
-- Costs kept close together so Tower B's overall spread stays < 30%
-- (Q19 should NOT flag Tower B for any category).
('ZN000008', '2024-01-01', 22500.00, 'Operational', FALSE, 'K0004', 'N0001'),  -- Microscope
('ZN000009', '2024-01-05', 10200.00, 'Operational', TRUE,  'K0004', 'N0002'),  -- Centrifuge
('ZN000010', '2024-01-10', 26500.00, 'Operational', FALSE, 'K0004', 'N0003'),  -- Spectrometer
('ZN000011', '2024-01-15', 11000.00, 'Operational', FALSE, 'K0004', 'N0004');  -- Thermocycler

-- ============================================================
-- RESEARCH PROJECTS (minimal -- not directly queried by Lab 4, but
-- Reservation.ProjectCode is nullable so this is optional support data)
-- ============================================================
INSERT INTO ResearchProject (ProjectCode, Title, StartDate, EndDate, FundingSource, Status) VALUES
('ZP0001', 'Nanomaterial Synthesis', '2025-01-01', '2026-12-31', 'Internal', 'Active');

-- ============================================================
-- RESERVATIONS -- the date-relative core of this seed.
--
-- Q4  "next 7 days"   : PlannedStartTime in (CURDATE(), CURDATE()+7]
-- Q11 "next 30 days"  : research users with NO reservation in that window
-- Q16 "next reservation date per research user" : MIN(future PlannedStartTime)
-- Q17 ">=2 reservations AND latest within last 14 days"
-- Q18 "approved reservations in last 90 days, ranked per building"
-- Q10 "count by status (Approved/Pending/Cancelled) per lab, single result"
-- ============================================================
INSERT INTO Reservation (ReservationID, SubmissionTimestamp, PlannedStartTime, PlannedEndTime, Purpose, Status, PersonID, SerialNumber, ProjectCode, ApprovedBy) VALUES
-- --- Q4 target: reservations within the NEXT 7 days (from K0001/K0002 units) ---
('ZR0001', NOW(), CURDATE() + INTERVAL 2 DAY, CURDATE() + INTERVAL 2 DAY + INTERVAL 2 HOUR, 'Imaging', 'Approved', 'Z00001', 'ZN000001', 'ZP0001', 'Z00007'),
('ZR0002', NOW(), CURDATE() + INTERVAL 6 DAY, CURDATE() + INTERVAL 6 DAY + INTERVAL 2 HOUR, 'Spectrometry', 'Pending',  'Z00002', 'ZN000004', NULL, NULL),
-- a reservation just OUTSIDE the 7-day window (day 9) -- must NOT appear in Q4
('ZR0003', NOW(), CURDATE() + INTERVAL 9 DAY, CURDATE() + INTERVAL 9 DAY + INTERVAL 2 HOUR, 'Centrifuge run', 'Approved', 'Z00003', 'ZN000006', NULL, NULL),

-- --- Q11 / Q16: research-user reservation horizon ---
-- Z00004 has a reservation in 20 days (within next 30 -> excluded from Q11)
('ZR0004', NOW(), CURDATE() + INTERVAL 20 DAY, CURDATE() + INTERVAL 20 DAY + INTERVAL 1 HOUR, 'Routine', 'Pending', 'Z00004', 'ZN000005', NULL, NULL),
-- Z00005 has a reservation in 45 days (OUTSIDE next 30 -> Z00005 has no
-- reservation in the next 30 days, so Z00005 SHOULD appear in Q11)
('ZR0005', NOW(), CURDATE() + INTERVAL 45 DAY, CURDATE() + INTERVAL 45 DAY + INTERVAL 1 HOUR, 'Routine', 'Pending', 'Z00005', 'ZN000008', NULL, NULL),
-- Z00006, Z00008 have NO future reservation at all -> also appear in Q11
-- (Z00001, Z00002, Z00003 are excluded from Q11 via ZR0001/ZR0002/ZR0003 above)

-- --- Q17: >=2 reservations, latest within last 14 days ---
-- Z00006: 3 PAST reservations, most recent 5 days ago (within last 14 -> qualifies)
('ZR0006', NOW(), CURDATE() - INTERVAL 40 DAY, CURDATE() - INTERVAL 40 DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00006', 'ZN000007', NULL, NULL),
('ZR0007', NOW(), CURDATE() - INTERVAL 20 DAY, CURDATE() - INTERVAL 20 DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00006', 'ZN000007', NULL, NULL),
('ZR0008', NOW(), CURDATE() - INTERVAL 5  DAY, CURDATE() - INTERVAL 5  DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00006', 'ZN000007', NULL, NULL),
-- Z00007: 2 PAST reservations, most recent 25 days ago (outside last 14 -> excluded)
('ZR0009', NOW(), CURDATE() - INTERVAL 60 DAY, CURDATE() - INTERVAL 60 DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00007', 'ZN000009', NULL, NULL),
('ZR0010', NOW(), CURDATE() - INTERVAL 25 DAY, CURDATE() - INTERVAL 25 DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00007', 'ZN000009', NULL, NULL),
-- Z00008: only 1 reservation ever, 3 days ago (fails ">=2 reservations" -> excluded)
('ZR0011', NOW(), CURDATE() - INTERVAL 3 DAY, CURDATE() - INTERVAL 3 DAY + INTERVAL 1 HOUR, 'Routine', 'Completed', 'Z00008', 'ZN000010', NULL, NULL),

-- --- Q18: approved reservations in the LAST 90 days, ranked per building ---
-- Tower A (K0001, K0002): K0001 gets 3 approved in last 90 days, K0002 gets 1
('ZR0012', NOW(), CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 10 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00001', 'ZN000001', NULL, 'Z00007'),
('ZR0013', NOW(), CURDATE() - INTERVAL 30 DAY, CURDATE() - INTERVAL 30 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00001', 'ZN000002', NULL, 'Z00007'),
('ZR0014', NOW(), CURDATE() - INTERVAL 50 DAY, CURDATE() - INTERVAL 50 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00002', 'ZN000001', NULL, 'Z00007'),
('ZR0015', NOW(), CURDATE() - INTERVAL 15 DAY, CURDATE() - INTERVAL 15 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00002', 'ZN000004', NULL, 'Z00007'),
-- an approved reservation OUTSIDE the 90-day window (must not count for Q18)
('ZR0016', NOW(), CURDATE() - INTERVAL 120 DAY, CURDATE() - INTERVAL 120 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00001', 'ZN000005', NULL, 'Z00004'),
-- Tower B (K0003, K0004): K0004 gets 2 approved in last 90 days, K0003 gets 0
('ZR0017', NOW(), CURDATE() - INTERVAL 5  DAY, CURDATE() - INTERVAL 5  DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00006', 'ZN000008', NULL, 'Z00007'),
('ZR0018', NOW(), CURDATE() - INTERVAL 25 DAY, CURDATE() - INTERVAL 25 DAY + INTERVAL 1 HOUR, 'Routine', 'Approved', 'Z00007', 'ZN000009', NULL, 'Z00007'),

-- --- Q10: status counts per lab (Approved/Pending/Cancelled) in one result ---
-- K0001 already has Approved x3 (ZR0001 was Approved... wait it's day+2,
-- still counts regardless of date for Q10, which is NOT date-filtered)
('ZR0019', NOW(), CURDATE() - INTERVAL 2 DAY,  CURDATE() - INTERVAL 2 DAY + INTERVAL 1 HOUR,  'Routine', 'Cancelled', 'Z00003', 'ZN000002', NULL, NULL),
('ZR0020', NOW(), CURDATE() - INTERVAL 1 DAY,  CURDATE() - INTERVAL 1 DAY + INTERVAL 1 HOUR,  'Routine', 'Pending',   'Z00004', 'ZN000003', NULL, NULL);

-- ============================================================
-- Q20 data-quality violation, fully isolated in K0005/Annex C so it
-- never participates in Q5/Q6/Q9/Q14/Q15/Q18/Q19's carefully-tuned
-- Building/Category groupings. Without at least one genuine violation,
-- Q20's correct answer would be an empty result set -- indistinguishable
-- from a blank/unanswered query (see test_lab4.py's _is_effectively_blank
-- guard, which independently covers this regardless).
-- ============================================================
INSERT INTO EquipmentUnit (SerialNumber, AcquisitionDate, PurchaseCost, CurrentStatus, IsPortable, LabID, ModelID) VALUES
('ZN000012', '2023-06-01', -50.00, 'Operational', TRUE, 'K0005', 'N0002');
