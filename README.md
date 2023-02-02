This Git repo is a port of this Airflow DAG:

https://github.com/Greenstand/treetracker-airflow-dags/blob/main/map/assign-new-trees-to-clusters.py

to Prefect as a means of evaluating Prefect as an orchestration tool.

To get Prefect up and running:

Sign up for a free Prefect Cloud account (Personal tier https://www.prefect.io/pricing/):

- https://app.prefect.cloud/auth/login

and get invited to the treetracker-prefect-dev Workspace

This workspace has all the Prefect Blocks correctly set up. Think of Prefect Blocks as Airflow Variables and Operators combined into one. For the above workspace, the Airflow Variables from Greenstand's dev Airflow have been ported over to Prefect. A Slack Webhook block has also been set up so that notifications of data pipeline completion can be sent to a Slack channel.

![alt text](https://github.com/huang-pan/treetracker-prefect/blob/master/prefect%20blocks.png?raw=true)


The instructions below are for macOS:

https://docs.prefect.io/getting-started/installation/
- Make sure you have python 3 installed
- pip3 install -U prefect
- Create an API key in Prefect Cloud: https://docs.prefect.io/ui/cloud-getting-started/#create-an-api-key. The API key will be used in the 'prefect cloud login' command below.
- prefect cloud login

Clone this git repo and cd to the cloned repo directory. For example:

- cd ~/Greenstand/git/treetracker-prefect

The below instructions are for a local deployment. Your computer is used to run the Prefect Flows (similar to Airflow DAGs). The assign-tree-flow is run. It is a direct port of the assign_tree_to_cluster DAG.
- export PYTHONPATH=${PYTHONPATH}:./:./flows:./flows/map
- python deployment.py
- prefect agent start -q 'assign_tree_flow_queue' &
- python flows/map/assign_tree_to_cluster.py

You can also play around with the flow and deployment from the Prefect Cloud UI and compare it with the Airflow webserver UI. You can also schedule flow runs from the Prefect Cloud UI.

![alt text](https://github.com/huang-pan/treetracker-prefect/blob/master/prefect%20flow%20runs.png?raw=true)


The structure of this git repo is copied from: https://github.com/anna-geller/prefect-dataplatform: an excellent example of how you would use Prefect, dbt, and Snowflake: https://medium.com/the-prefect-blog/modular-data-stack-build-a-data-platform-with-prefect-dbt-and-snowflake-9e8ef6a56503

This git repo was just a proof of concept of using Prefect instead of Airflow as a workflow orchestration tool.

Further things to do if we were serious about upgrading from Airflow to Prefect for Greenstand:

- Install Prefect on Greenstand's dev and prod Kubernetes clusters using Ansible and the Prefect Helm chart: https://github.com/PrefectHQ/prefect-helm similar to this: https://github.com/Greenstand/treetracker-infrastructure/tree/master/airflow
  - Prefect agents, work queues, etc. will be on deployed to k8s pods, see https://discourse.prefect.io/t/deploying-prefect-agents-on-kubernetes/1298
  - Also see: https://medium.com/the-prefect-blog/prefect-2-4-1-adds-k8s-agent-manifest-improved-helm-charts-notifications-firebolt-integration-5eec23f6f0ae
- https://medium.com/the-prefect-blog/how-to-use-kubernetes-with-prefect-419b2e8b8cb2
    - Create a Kubernetes deployment using Greenstand's Digital Ocean k8s (dev / prod) for Prefect agent, work queue. Prefect agents are like Airflow schedulers. Prefect work queues are like Airflow worker pods.
	    - Set the initial deployment schedules in the deployment.py file
    - Add S3 storage for logs of flow runs
- Add block files for connections, variables, secrets, etc.: https://docs.prefect.io/concepts/blocks/
	- only need to do once, can do from UI
	- https://medium.com/the-prefect-blog/modular-data-stack-build-a-data-platform-with-prefect-dbt-and-snowflake-part-3-7c325a8b63dc
- Add prod workspace in Prefect Cloud, and dev / prod switches to deployment.py

Notes:
- Differences between self hosted Prefect UI (Prefect Orion server) and managed Prefect UI (Prefect Cloud): https://docs.prefect.io/ui/cloud/
	- Prefect Cloud has user accounts, workspaces, automations, organizations, RBAC, etc.
	- Also see: https://medium.com/the-prefect-blog/how-to-self-host-prefect-orion-with-postgres-using-docker-compose-631c41ab8a9f
- Prefect can run scripts through shell commmands: https://discourse.prefect.io/t/prefect-collection-to-run-shell-commands-in-your-flows-prefect-shell/874
- Prefect can also run Flows on Docker images provisioned to Kubernetes: 
  - Create Docker image and then run Flow code using Docker image: https://medium.com/the-prefect-blog/how-to-use-kubernetes-with-prefect-part-2-2e98cdb91c7e
  - Run flow code baked into Docker image: https://medium.com/the-prefect-blog/how-to-use-kubernetes-with-prefect-part-3-e2223ce34ba7
  - This method replicates what the Airflow KubernetesPodOperator does: 
  	- https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html
	- https://github.com/Greenstand/treetracker-airflow-dags/blob/main/migrate_stakeholders_dag.py
	- https://github.com/Kpoke/domain-migration-scripts/tree/fix/migration/v1Tov2Migrations


Airflow vs Prefect:
- Airflow is very customizable and powerful, at the expense of a lot of boilerplate code
- Prefect is the second generation of workflow orchestration tools, and it shows. DAGs are optional - flows can be triggered by API calls, etc. The Prefect UI is a lot cleaner than the Airflow UI. Prefects components are cloud native, modular, and composable. Everything is modularized according to well thought through boundaries in Prefect. Switching from dev to prod environments is super easy in Prefect, whereas in Airflow it's very clunky. In general, Prefect is much easier to use and easier to learn than Airflow.
- If I was starting from scratch, I'd use Prefect instead of Airflow. However, since Greenstand already has a lot invested in its Airflow infrastructure, the benefits of Prefect are not enough to warrant a swtich from Airflow to Prefect for Greenstand. Greenstand is also not willing to pay for Prefect Cloud.
