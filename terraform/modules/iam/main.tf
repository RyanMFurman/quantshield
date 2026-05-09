data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  # Keep IAM names consistent with the rest of the Terraform stack.
  name_prefix = "${var.project_name}-${var.environment}"

  # CloudWatch Logs write permissions stay limited to explicitly configured Lambda functions.
  lambda_log_group_arns = [
    for function_name in var.lambda_function_names :
    "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${function_name}:*"
  ]

  # CreateLogGroup uses the log group ARN without the trailing stream wildcard.
  lambda_log_group_create_arns = [
    for function_name in var.lambda_function_names :
    "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${function_name}"
  ]

  # GitHub's OIDC subject pins deploy access to this repository and the allowed refs.
  github_subjects = [
    for ref in var.github_allowed_refs :
    "repo:${var.github_repository}:ref:${ref}"
  ]

  # Use an existing provider when supplied, otherwise reference the provider this module creates.
  github_oidc_provider_arn = coalesce(
    var.github_oidc_provider_arn,
    try(aws_iam_openid_connect_provider.github[0].arn, null)
  )
}

# Creates the GitHub Actions OIDC provider only when the account does not already manage one elsewhere.
resource "aws_iam_openid_connect_provider" "github" {
  count = var.github_oidc_provider_arn == null ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = var.github_oidc_thumbprints

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-github-actions-oidc"
  })
}

# Lambda can assume only the Lambda execution role.
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Execution role for application Lambda functions.
resource "aws_iam_role" "lambda" {
  name               = "${local.name_prefix}-lambda-role"
  description        = "Least-privilege Lambda execution role for ${local.name_prefix} functions."
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-lambda-role"
  })
}

# Lambda logging policy avoids AWSLambdaBasicExecutionRole so log resources stay scoped.
data "aws_iam_policy_document" "lambda_logs" {
  statement {
    sid = "WriteLambdaLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = local.lambda_log_group_arns
  }

  statement {
    sid       = "CreateConfiguredLambdaLogGroups"
    actions   = ["logs:CreateLogGroup"]
    resources = local.lambda_log_group_create_arns
  }
}

# Customer-managed policy documents the exact CloudWatch Logs permissions Lambda receives.
resource "aws_iam_policy" "lambda_logs" {
  name        = "${local.name_prefix}-lambda-logs"
  description = "Allows Lambda functions to create and write only their configured CloudWatch log groups."
  policy      = data.aws_iam_policy_document.lambda_logs.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-lambda-logs"
  })
}

# Attach the scoped log policy to the Lambda execution role.
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_logs.arn
}

# EC2 can assume only the EC2 instance role.
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

# Instance role used by EC2 workloads in this environment.
resource "aws_iam_role" "ec2" {
  name               = "${local.name_prefix}-ec2-role"
  description        = "Least-privilege EC2 instance role for ${local.name_prefix} compute."
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-ec2-role"
  })
}

# SSM messaging APIs require Resource "*" because AWS does not support resource-level scoping here.
data "aws_iam_policy_document" "ec2_ssm" {
  statement {
    sid = "SystemsManagerCoreChannels"
    actions = [
      "ssm:UpdateInstanceInformation",
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
      "ec2messages:AcknowledgeMessage",
      "ec2messages:DeleteMessage",
      "ec2messages:FailMessage",
      "ec2messages:GetEndpoint",
      "ec2messages:GetMessages",
      "ec2messages:SendReply"
    ]
    resources = ["*"]
  }
}

# Enables Systems Manager connectivity without granting broad EC2 or admin permissions.
resource "aws_iam_policy" "ec2_ssm" {
  name        = "${local.name_prefix}-ec2-ssm-core"
  description = "Allows EC2 instances to use AWS Systems Manager core messaging APIs."
  policy      = data.aws_iam_policy_document.ec2_ssm.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-ec2-ssm-core"
  })
}

# Attach SSM core messaging access to the EC2 role.
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.ec2_ssm.arn
}

# Instance profile exposes the EC2 role to launched instances.
resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2.name

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-ec2-profile"
  })
}

# GitHub Actions assumes the deploy role via OIDC, with audience and repository/ref checks.
data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.github_subjects
    }
  }
}

# Deploy role used by GitHub Actions workflows after OIDC trust validation.
resource "aws_iam_role" "github_actions_deploy" {
  name               = "${local.name_prefix}-github-actions-deploy"
  description        = "GitHub Actions deploy role restricted to ${var.github_repository} and configured refs."
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-github-actions-deploy"
  })
}

# Deployment permissions cover only the Terraform-managed resource families in this repo.
data "aws_iam_policy_document" "github_actions_deploy" {
  statement {
    sid = "ManageProjectNetworkingAndCompute"
    actions = [
      "ec2:AssociateRouteTable",
      "ec2:AttachInternetGateway",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateInternetGateway",
      "ec2:CreateRoute",
      "ec2:CreateRouteTable",
      "ec2:CreateSecurityGroup",
      "ec2:CreateSubnet",
      "ec2:CreateTags",
      "ec2:CreateVpc",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteRoute",
      "ec2:DeleteRouteTable",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteSubnet",
      "ec2:DeleteTags",
      "ec2:DeleteVpc",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:DetachInternetGateway",
      "ec2:DisassociateRouteTable",
      "ec2:ModifySubnetAttribute",
      "ec2:ModifyVpcAttribute",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:RunInstances",
      "ec2:TerminateInstances"
    ]
    resources = ["*"]
  }

  statement {
    sid = "ManageProjectIamRoles"
    actions = [
      "iam:AttachRolePolicy",
      "iam:CreateInstanceProfile",
      "iam:CreateOpenIDConnectProvider",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:DeleteInstanceProfile",
      "iam:DeleteOpenIDConnectProvider",
      "iam:DeletePolicy",
      "iam:DeletePolicyVersion",
      "iam:DeleteRole",
      "iam:DeleteRolePolicy",
      "iam:DetachRolePolicy",
      "iam:GetInstanceProfile",
      "iam:GetOpenIDConnectProvider",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListInstanceProfilesForRole",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:PassRole",
      "iam:PutRolePolicy",
      "iam:RemoveRoleFromInstanceProfile",
      "iam:AddRoleToInstanceProfile",
      "iam:TagInstanceProfile",
      "iam:TagOpenIDConnectProvider",
      "iam:TagPolicy",
      "iam:TagRole",
      "iam:UntagInstanceProfile",
      "iam:UntagOpenIDConnectProvider",
      "iam:UntagPolicy",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy"
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:instance-profile/${local.name_prefix}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.name_prefix}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.name_prefix}-*"
    ]

    # PassRole is limited to EC2 and Lambda; the condition is ignored for non-PassRole IAM APIs.
    condition {
      test     = "StringEqualsIfExists"
      variable = "iam:PassedToService"
      values = [
        "ec2.amazonaws.com",
        "lambda.amazonaws.com"
      ]
    }
  }
}

# Customer-managed deploy policy avoids AdministratorAccess and wildcard IAM/EC2 actions.
resource "aws_iam_policy" "github_actions_deploy" {
  name        = "${local.name_prefix}-github-actions-deploy"
  description = "Allows GitHub Actions to deploy only QuantShield ${var.environment} Terraform-managed resources."
  policy      = data.aws_iam_policy_document.github_actions_deploy.json

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-github-actions-deploy"
  })
}

# Attach deploy permissions to the GitHub Actions role.
resource "aws_iam_role_policy_attachment" "github_actions_deploy" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.github_actions_deploy.arn
}
