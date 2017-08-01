CREATE OR REPLACE FUNCTION updateStatusCount() RETURNS trigger AS $updateStatus$
		DECLARE
			old_status_count integer;
		BEGIN
			SELECT numflights into old_status_count
			FROM NumberOfFlightsTaken
			WHERE customerid = NumberOfFlightsTaken.customerid;
		
			IF (TG_OP = 'INSERT') THEN
				IF EXISTS (SELECT customerid from NumberOfFlightsTaken
				    WHERE customerid = NEW.customerid) THEN
					UPDATE NumberOfFlightsTaken
					SET numflights = numflights + 1
					WHERE customerid = NEW.customerid;
				ELSE
					INSERT INTO NumberOfFlightsTaken
					(customerid, customername, numflights)
					values(NEW.customerid,
						(SELECT customers.name
						FROM customers
						WHERE customers.customerid = NEW.customerid), 1);
                RETURN NEW;
				END IF;
		
			ELSEIF (TG_OP = 'DELETE' AND old_status_count = 1) THEN
				DELETE FROM NumberOfFlightsTaken
				WHERE customerid = OLD.customerid;
			ELSEIF (TG_OP = 'DELETE' AND old_status_count > 1) THEN
				UPDATE NumberOfFlightsTaken
				SET numflights = numflights - 1
				WHERE customerid = OLD.customerid;
			END IF;
			RETURN OLD;
		END;
$updateStatus$ LANGUAGE plpgsql;

CREATE TRIGGER update_num_status AFTER 
INSERT OR DELETE ON flewon 
FOR EACH ROW EXECUTE PROCEDURE updateStatusCount();
END;
