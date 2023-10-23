

provider "sysdig" {
  sysdig_secure_api_token = var.sysdig_secure_api_token #"65ad0f94-4d2b-4323-94ed-e5d207140998"
}
data "sysdig_fargate_workload_agent" "instrumented" {
  container_definitions = jsonencode([
            {
                "name": "sleep",
                "image": "dockerbadboy/art",
                "cpu": 1,
                "memory": 10,
                "portMappings": [],
                "essential": true,
                "command": [
                    "sleep",
                    "360"
                ],
                "environment": [],
                "mountPoints": [],
                "volumesFrom": []
            }
        ],

)

  sysdig_access_key     = var.sysdig_access_key #"4667a741-a377-4116-9319-6c50d57dfe99"

  workload_agent_image  = "quay.io/sysdig/workload-agent:latest"

  orchestrator_host     = var.orchestrator_host #"collector.sysdigcloud.com"
  orchestrator_port     = var.orchestrator_port #6443
}

resource "aws_ecs_task_definition" "fargate_task" {
  memory = "1024"
  cpu = "512"
  family = "sleep360"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  container_definitions    = "${data.sysdig_fargate_workload_agent.instrumented.output_container_definitions}"
}
