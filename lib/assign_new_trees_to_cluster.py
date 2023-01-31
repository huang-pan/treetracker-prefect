import datetime
import psycopg2
from prefect import get_run_logger

def assign_new_trees_to_cluster(conn, dry_run = True):
    logger = get_run_logger()
    logger.info("assign new trees to cluster...")

    # assign current time to variable
    very_start = datetime.datetime.now()
    start = datetime.datetime.now()

    # execute query
    cur = conn.cursor()
    cur.execute("""
      SELECT count(id)
      FROM trees
      WHERE trees.active = true
      AND trees.cluster_regions_assigned = false
    """)
    logger.info("SQL result:" + cur.query.decode())
    # get result
    count = cur.fetchone()[0]
    logger.info("count of tree that needs to assign to cluster:" + str(count))
    if(count == 0):
        logger.info("no tree needs to assign to cluster")
        return

    # try/except block to catch errors
    try:
        # begin db transaction with isolation level READ COMMITTED
        # the whole job is in this read committed transaction, so this job
        # will just deal with the tree data that goes into DB before the
        # transaction is started, for the trees that will go into the DB 
        # after this transaction is started, the job will be done in the
        # next round of schedule.
        conn.set_isolation_level(0)
        # cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)

        start = datetime.datetime.now()
        insertSQL = """
            INSERT INTO tree_region
            (tree_id, zoom_level, region_id)
            SELECT DISTINCT ON (trees.id, zoom_level) trees.id AS tree_id, zoom_level, region.id
            FROM (
                SELECT *
                FROM trees
                WHERE trees.active = true
                AND trees.cluster_regions_assigned = false
                ---LIMIT 1000
            ) trees
            JOIN region
            ON ST_Contains( region.geom, trees.estimated_geometric_location)
            JOIN region_zoom
            ON region_zoom.region_id = region.id
            ORDER BY trees.id, zoom_level, region_zoom.priority DESC
        """
        # logger.info("insertSQL:" + insertSQL)
        cur.execute(insertSQL)
        logger.info("SQL result:" + cur.query.decode())
        logger.info("inserted rows:" + str(cur.rowcount))
        # quit if rows inserted is 0
        if cur.rowcount == 0:
            logger.info("no tree needs to assign to cluster")
            return

        logger.info("time elapsed:" + str(datetime.datetime.now() - start))
        start = datetime.datetime.now()

        # update all trees that are assigned to cluster
        updateSQL = """
            UPDATE trees
            SET cluster_regions_assigned = true
            FROM tree_region
            WHERE tree_region.tree_id = trees.id
            AND cluster_regions_assigned = false
        """
        # logger.info("updateSQL:", updateSQL)
        cur.execute(updateSQL)
        logger.info("SQL result:" + cur.query.decode())
        logger.info("updated rows:" + str(cur.rowcount))

        # logger.info time elapsed
        logger.info("time elapsed:" + str(datetime.datetime.now() - start))
        start = datetime.datetime.now()

        logger.info("update materialized views...")
        updateMaterializedViewSQL = """
            REFRESH MATERIALIZED VIEW CONCURRENTLY active_tree_region
        """
        cur.execute(updateMaterializedViewSQL)

        logger.info("time elapsed:" + str(datetime.datetime.now() - start))
        start = datetime.datetime.now()

        # SQL
        zoomLevel14SQL = """
            SELECT 'cluster' AS type,
            St_centroid(clustered_locations) centroid,
            St_numgeometries(clustered_locations) count
            FROM
            (
            SELECT Unnest(St_clusterwithin(estimated_geometric_location, 0.005)) clustered_locations
            FROM   trees
            WHERE  active = true
            ) clusters
        """
        cur.execute(zoomLevel14SQL)

        logger.info("time elapsed:" + str(datetime.datetime.now() - start))
        start = datetime.datetime.now()

        # get all rows
        rows = cur.fetchall()
        logger.info("rows count:" + str(len(rows)))
        zoomLevel = 14
        deleteZoomLevelSQL = f"""
            DELETE FROM clusters WHERE zoom_level = {zoomLevel}
        """
        cur.execute(deleteZoomLevelSQL)

        # go through each row with index
        for index, row in enumerate(rows):
            insertSQL = """
                INSERT INTO clusters (count, zoom_level, location) values (%s, %s, %s) RETURNING *
            """
            # execute sql
            cur.execute(insertSQL, (row[2], zoomLevel, row[1]))

            # logger.info every 100 rows
            if(index % 100 == 0):
                logger.info("inserted" + str(index) + "rows")

        # commit transaction
        if(dry_run == False):
            conn.commit()
            logger.info("transaction committed")
        else:
            logger.info("transaction rollback for dry run")
            conn.rollback()
    except Exception as e:
        logger.info("Error:", e)
        conn.rollback()

    # print time elapsed
    logger.info("total time elapsed:" + str(datetime.datetime.now() - very_start))

    return True