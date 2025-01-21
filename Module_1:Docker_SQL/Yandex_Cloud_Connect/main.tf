terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  zone = "<default_availability_zone>"
}

resource "yandex_storage_bucket" "test" {
  bucket = "tf-test-bucket"
}