# Run Terraform in Docker Container
## Vanilla Docker
Build image _terraform-yc_ from _Dockerfile_, where entrypoint is set to _terraform_, so one can run the following commands to manage cloud resources in Yandex Cloud. The authentication information is passed via environment variables. 
```
docker run --rm \ 
-e YC_TOKEN=$YC_TOKEN -e YC_CLOUD_ID=$YC_CLOUD_ID -e YC_FOLDER_ID=$YC_FOLDER_ID \ 
-v terraform_volume:/terraform terraform-yc init
```
```
docker run --rm \ 
-e YC_TOKEN=$YC_TOKEN -e YC_CLOUD_ID=$YC_CLOUD_ID -e YC_FOLDER_ID=$YC_FOLDER_ID \ 
-v terraform_volume:/terraform terraform-yc plan
```
```
docker run --rm \ 
-e YC_TOKEN=$YC_TOKEN -e YC_CLOUD_ID=$YC_CLOUD_ID -e YC_FOLDER_ID=$YC_FOLDER_ID \ 
-v terraform_volume:/terraform terraform-yc apply -auto-approve
```
```
docker run --rm \ 
-e YC_TOKEN=$YC_TOKEN -e YC_CLOUD_ID=$YC_CLOUD_ID -e YC_FOLDER_ID=$YC_FOLDER_ID \ 
-v terraform_volume:/terraform terraform-yc destroy -auto-approve
```
## Using Docker Compose
Let's build terraform-yc image from Dockerfile
```
docker compose build 
```
Run particular terraform command, the environment variables for authentication must be set in the terminal beforehand as _docker-compose.yaml_ uses them to pass into the container. 
```
docker compose run  --rm erraform-yc init
```
```
docker compose run  --rm erraform-yc plan
```
```
docker compose run  --rm erraform-yc apply -auto-approve
```
```
docker compose run  --rm erraform-yc destroy -auto-approve
```



