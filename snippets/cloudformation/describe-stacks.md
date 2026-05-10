CloudFormation スタックの詳細を確認する。

```bash
aws cloudformation describe-stacks \
    --stack-name {{ stack_name }} \
    --region {{ region }}
```

スタックが存在する場合の結果例:
```output
{
    "Stacks": [
        {
            "StackName": "{{ stack_name }}",
            "StackId": "arn:aws:cloudformation:{{ region }}:123456789012:stack/{{ stack_name }}/12345678-1234-1234-1234-123456789012",
            "StackStatus": "CREATE_COMPLETE",
            "CreationTime": "2026-05-10T10:00:00.000000+00:00",
            "Description": "Training stack - S3 bucket with environment tagging",
{% if stack_parameters %}
            "Parameters": [
{% for p in stack_parameters %}
                {
                    "ParameterKey": "{{ p.key }}",
                    "ParameterValue": "{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}"
                }{{ ',' if not loop.last else '' }}
{% endfor %}
            ],
{% endif %}
            "Outputs": [
                {
                    "OutputKey": "BucketName",
                    "OutputValue": "{{ stack_name }}-trainingbucket-abc123"
                },
                {
                    "OutputKey": "BucketArn",
                    "OutputValue": "arn:aws:s3:::{{ stack_name }}-trainingbucket-abc123"
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "{{ stack_name }}"
                }
            ]
        }
    ]
}
```

スタックが存在しない場合の結果例:
```output
An error occurred (ValidationError) when calling the DescribeStacks operation: Stack with id {{ stack_name }} does not exist
```
