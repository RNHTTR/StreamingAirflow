Hacky Airflow Streaming
========

This project uses the [Astro CLI](https://github.com/astronomer/astro-cli) to quickly get Apache Airflow up & running. It uses an asynchronous version of the KubernetesPodOperator, i.e. [`KubernetesPodOperatorAsync`](https://registry.astronomer.io/providers/astronomer-providers/modules/kubernetespodoperatorasync) along with a [custom timetable](https://airflow.apache.org/docs/apache-airflow/stable/howto/timetable.html) to allow for streaming applications running on Airflow without consuming Airflow native resources (e.g. [pool slots](https://airflow.apache.org/docs/apache-airflow/stable/concepts/pools.html), [parallelism](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#parallelism)).

Project Contents
================

In addition to other useful built-ins that ship with `astro dev init`, the project contains the following files and folders:

- dags: This folder contains the Python files for Airflow DAGs. The example streaming DAG is `streamingdag.py`.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.

Deploy Your Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 3 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks

2. Verify that all 3 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either stop your existing Docker containers or change the port.

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.
