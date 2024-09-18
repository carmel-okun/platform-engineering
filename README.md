# platform-engineering

## Installing dependencies
### source: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

sudo apt install unzip

unzip awscliv2.zip

sudo ./aws/install



## Installing Jenkins
### source: https://www.jenkins.io/doc/book/installing/linux/#debianubuntu

sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt-get update

sudo apt-get install jenkins



## Installing JAVA

sudo apt update

sudo apt install fontconfig openjdk-17-jre

java -version

openjdk version "17.0.8" 2023-07-18

sudo snap install openjdk

OpenJDK Runtime Environment (build 17.0.8+7-Debian-1deb12u1)
** does not work, but should not matter

OpenJDK 64-Bit Server VM (build 17.0.8+7-Debian-1deb12u1, mixed mode, sharing)
** does not work, but should not matter



## Start Jenkins

sudo systemctl enable jenkins

sudo systemctl start jenkins

sudo systemctl status jenkins

http://<public_ip>:8080

sudo cat /var/lib/jenkins/secrets/initialAdminPassword



## jenkins plugins

download: AWS Credentials, Pipeline: AWS Steps

create: AWS Credentials named "AWS Credentials"
