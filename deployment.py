# deployment.py
from flows.map.assign_tree_to_cluster import assign_tree_flow
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=assign_tree_flow,
    name="assign_tree_flow-local",
    work_queue_name="assign_tree_flow_queue",
)

if __name__ == "__main__":
    deployment.apply()
