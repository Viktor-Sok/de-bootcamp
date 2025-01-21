## Q1
`Dockerfile-python-3.12.8` - Dockerfile to build an image. \
`docker-commands.sh` - bash script to build docker image and run the container.\
`Answer.txt` - answer to the question.

## Q2
`docker-compose.yaml` - run postgres and pgadmin containers.\
Accessing postgres from pgadmin: `postgres:5432`

## Q3-Q6
Sql queries.

## Q7
Bash script for terraform basic usage.

### NB1: Data ingestion into DB
1. Build docker image named `ingest_data:1.0` based on `Dockerfile` and `data_ingest.py` 
2. Run `docker-compose.yaml`.

### NB2: Connect to Yandex Cloud (YC) and create simple bucket for test.
Setting up environment to work with YC:
1. Follow the [instructions](https://yandex.cloud/en/docs/tutorials/infrastructure-management/terraform-quickstart#console_1) to start working with YC. 
2. Create [Service account](https://yandex.cloud/en/docs/iam/concepts/users/service-accounts).
3. Set up command line [interface](https://yandex.cloud/en/docs/cli/quickstart#install).

Managing YC using terraform:
1. Refresh access keys in environment variables
```
export YC_TOKEN=$(yc iam create-token)
export YC_CLOUD_ID=$(yc config get cloud-id)
export YC_FOLDER_ID=$(yc config get folder-id)
```
2. Now, you can use terraform `terraform init`, etc.

`main.tf` - creates YC bucket named `test`



