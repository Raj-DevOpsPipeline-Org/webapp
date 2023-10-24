packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-west-1"
}

variable "source_ami" {
  type    = string
  default = "ami-071175b60c818694f"
}

variable "ssh_username" {
  type    = string
  default = "admin"
}

variable "subnet_id" {
  type    = string
  default = "subnet-08254c98cf986a4dc"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "volume_size" {
  type    = number
  default = 8
}

variable "volume_type" {
  type    = string
  default = "gp2"
}

// variable "ami_regions" {
//   type    = list(string)
//   default = ["us-west-1"]
// }



variable "ami_users" {
  type    = list(string)
  default = ["475169959315"]
}

variable "DB_PASSWORD" {
  type    = string
  default = ""
}

variable "FLASK_APP" {
  type    = string
  default = ""
}

variable "FLASK_DEBUG" {
  type    = string
  default = ""
}

variable "DATABASE_URL" {
  type    = string
  default = ""
}

variable "CSV_PATH" {
  type    = string
  default = ""
}

source "amazon-ebs" "my-ami" {
  ami_name        = "csye6225_ami_${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  instance_type   = var.instance_type
  region          = var.aws_region
  ami_description = "AMI for CSYE 6225"
  source_ami      = var.source_ami
  ssh_username    = var.ssh_username
  subnet_id       = var.subnet_id
  ami_regions = [
    "us-west-1",
  ]
  ami_users = var.ami_users

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/xvda"
    volume_size           = var.volume_size
    volume_type           = var.volume_type
  }
}

build {
  sources = [
    "source.amazon-ebs.my-ami"
  ]

  provisioner "file" {
    source      = "webapp.zip"
    destination = "/tmp/webapp.zip"
  }


  provisioner "shell" {
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
      "CHECKPOINT_DISABLE=1",
      "DB_PASSWORD=${var.DB_PASSWORD}",
      "FLASK_APP=${var.FLASK_APP}",
      "FLASK_DEBUG=${var.FLASK_DEBUG}",
      "DATABASE_URL=${var.DATABASE_URL}",
      "CSV_PATH=${var.CSV_PATH}"
    ]
    script = "./setup.sh"
  }
}
