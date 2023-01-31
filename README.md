This Git repo is a port of this Airflow DAG:

https://github.com/Greenstand/treetracker-airflow-dags/blob/main/map/assign-new-trees-to-clusters.py
https://dev-k8s.treetracker.org/airflow/tree?dag_id=assign_tree_to_cluster

to Prefect as a means of evaluating Prefect as an orchestration tool.

To get Prefect up and running:

Sign up for a free Prefect Cloud account (Personal tier https://www.prefect.io/pricing/):

- https://app.prefect.cloud/auth/login

and get invited to the treetracker-prefect-dev Workspace

This workspace has all the Prefect Blocks correctly set up. Think of Prefect Blocks as Airflow Variables and Operators combined into one. For the above workspace, the Airflow Variables from https://dev-k8s.treetracker.org/airflow/variable/list/ have been ported over to Prefect. A Slack Webhook block has also been set up so that notifications of data pipeline completion can be sent to a Slack channel.


The instructions below are for macOS:

https://docs.prefect.io/getting-started/installation/
- Make sure you have python 3 installed
- pip install -U prefect
- prefect cloud login

Clone this git repo and cd to the cloned repo directory. For example:

- cd ~/Greenstand/git/treetracker-prefect

The below instructions is a local deployment. Your computer is used to run the Prefect Flows (similar to Airflow DAGs). The assign-tree-flow is run. It is a direct port of the assign_tree_to_cluster DAG.
- export PYTHONPATH=${PYTHONPATH}:./:./flows:./flows/map
- python deployment.py
- prefect agent start -q 'assign_tree_flow_queue'
- python flows/map/assign_tree_to_cluster.py

You can also play around with the flow and deployment from the Prefect Cloud UI and compare it with the Airflow webserver UI. You can also schedule flow runs from the Prefect Cloud UI.


The structure of this git repo is copied from this git repo: https://github.com/anna-geller/prefect-dataplatform

This project is an excellent example of how you would use Prefect, dbt, and Snowflake: https://medium.com/the-prefect-blog/modular-data-stack-build-a-data-platform-with-prefect-dbt-and-snowflake-9e8ef6a56503

This git repo was just a proof of concept of using Prefect instead of Airflow as an orchestration tool.

Further things to do if we were serious about upgrading from Airflow to Prefect for Greenstand:

https://medium.com/the-prefect-blog/how-to-use-kubernetes-with-prefect-419b2e8b8cb2
- Create a Kubernetes deployment using Greenstand's Digital Ocean k8s (dev / prod) for Prefect agent, work queue. Prefect agents are like Airflow schedulers. Prefect work queues are like Airflow worker pods.
	- Set the initial deployment schedules in the deployment.py file
- Add S3 storage for logs of flow runs
- Add block files for connections, variables, secrets, etc.: https://docs.prefect.io/concepts/blocks/
	- only need to do once, can do from UI
	- https://medium.com/the-prefect-blog/modular-data-stack-build-a-data-platform-with-prefect-dbt-and-snowflake-part-3-7c325a8b63dc
- Create a Prefect yaml file on https://github.com/Greenstand/treetracker-infrastructure to automatically deploy dev and prod Prefect agents, work queues, and web UIs on Greenstand's dev and prod Kubernetes clusters https://discourse.prefect.io/t/deploying-prefect-agents-on-kubernetes/1298
- Add prod workspace in Prefect Cloud, and dev / prod switches to deployment.py

Airflow vs Prefect:
- Airflow is very customizable and powerful, at the expense of a lot of boilerplate code
- Prefect is the second generation of workflow orchestration tools, and it shows. DAGs are optional - flows can be triggered by API calls, etc. The Prefect UI is a lot cleaner than the Airflow UI. Prefects components are cloud native and composable. Everything is modularized according to well thought through boundaries in Prefect. Switch from dev to prod environments is super easy in Prefect, whereas in Airflow it's very clunky. In general, Prefect is much easier to use and easier to learn than Airflow.
- If I was starting from scratch, I'd use Prefect instead of Airflow. However, since Greenstand already has a lot invested in its Airflow infrastructure, the benefits of Prefect are not enough to warrant a swtich from Airflow to Prefect for Greenstand.
