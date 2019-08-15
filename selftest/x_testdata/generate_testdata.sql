DROP SCHEMA IF EXISTS sqlrunner CASCADE;
DROP SCHEMA IF EXISTS d_testdev CASCADE;

CREATE SCHEMA sqlrunner;
CREATE SCHEMA d_testdev;

CREATE TABLE sqlrunner.test_data 
(
  col1   INT,
  col2   INT,
  col3   INT
);

INSERT INTO sqlrunner.test_data
VALUES
(
  1,
  2,
  3
);
