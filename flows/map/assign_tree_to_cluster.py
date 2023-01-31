import datetime
import psycopg2
from prefect import flow, task, get_run_logger
from prefect.blocks.notifications import SlackWebhook #import the SlackWebhook module
from prefect.blocks.system import String
from lib.assign_new_trees_to_cluster import assign_new_trees_to_cluster

@task
def assign_tree():
    logger = get_run_logger()
    DB_URL = String.load("database-url").value
    logger.info("DB_URL:" + DB_URL)
    conn = psycopg2.connect(DB_URL, sslmode='require')
    #db = PostgresHook(postgres_conn_id=postgresConnId, keepalives_idle=30)
    #conn = db.get_conn()  
    assign_new_trees_to_cluster(conn, False)

@flow()
def assign_tree_flow():
    slack_webhook_block = SlackWebhook.load("slack-notifications")
    assign_tree()
    # datetime object containing current date and time
    now = datetime.datetime.now()
    print("now =", now)
    slack_webhook_block.notify("assign_tree_to_cluster Done!")

if __name__ == "__main__":
    assign_tree_flow()
