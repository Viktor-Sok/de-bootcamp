FROM hashicorp/terraform:latest  
COPY .terraformrc /root/.terraformrc
WORKDIR /terraform
COPY main.tf main.tf  

ENTRYPOINT ["terraform"]
