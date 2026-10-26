USE company;

INSERT INTO EMPLOYEE
(ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES
('100000001', 'Ahmed', 'Ali', '2000-05-12', 'Alexandria', 'M', 8000.00, NULL),
('100000002', 'Mona', 'Hassan', '2001-08-20', 'Cairo', 'F', 7500.00, NULL),
('100000003', 'Omar', 'Khaled', '1999-11-03', 'Giza', 'M', 9000.00, NULL);

INSERT INTO DEPARTMENT
(Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES
(1, 'IT', '100000001', '2024-01-01'),
(2, 'HR', '100000002', '2025-02-01'),
(3, 'Finance', '100000003', '2026-03-01');

INSERT INTO PROJECT
(Pnumber, Pname, Plocation, Dno)
VALUES
(1, 'Website Development', 'Alexandria', 1),
(2, 'Employee Management', 'Cairo', 2),
(3, 'Financial System', 'Giza', 3);

UPDATE EMPLOYEE SET Dno = 1 WHERE ssn = '100000001';
UPDATE EMPLOYEE SET Dno = 2 WHERE ssn = '100000002';
UPDATE EMPLOYEE SET Dno = 3 WHERE ssn = '100000003';