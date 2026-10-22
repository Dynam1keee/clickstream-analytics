-- This PL/SQL block automatically creates a series of K-Means clustering models
-- with between 2 and 10 clusters. For each iteration, the algorithm settings are
-- configured, any existing model with the same name is dropped, and a new model
-- is created using the aggregated session data from USER_BEHAVIOR_VIEW.
%script
DECLARE
    v_setlist       DBMS_DATA_MINING.SETTING_LIST;
    v_model_name    VARCHAR2(50);
BEGIN
    FOR k IN 2..10 LOOP  -- Iterate from 2 to 10 clusters
        v_model_name := 'KM_USER_CLUS_' || TO_CHAR(k);

        BEGIN
            DBMS_DATA_MINING.DROP_MODEL(v_model_name);
        EXCEPTION WHEN OTHERS THEN NULL;
        END;

        v_setlist('ALGO_NAME')        := 'ALGO_KMEANS';
        v_setlist('PREP_AUTO')        := 'ON';
        v_setlist('KMNS_DISTANCE')    := 'KMNS_EUCLIDEAN';
        v_setlist('KMNS_DETAILS')     := 'KMNS_DETAILS_ALL';
        v_setlist('KMNS_ITERATIONS')  := '50';
        v_setlist('KMNS_NUM_BINS')    := '10';
        v_setlist('CLUS_NUM_CLUSTERS'):= TO_CHAR(k);

        DBMS_DATA_MINING.CREATE_MODEL2(
            MODEL_NAME          => v_model_name,
            MINING_FUNCTION     => 'CLUSTERING',
            DATA_QUERY          => 'select * from USER_BEHAVIOR_VIEW',
            SET_LIST            => v_setlist,
            CASE_ID_COLUMN_NAME => 'SESSION_ID');
    END LOOP;
END;