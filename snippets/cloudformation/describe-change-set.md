Change Set の詳細を確認する。

```bash
aws cloudformation describe-change-set \
    --stack-name {{ stack_name }} \
    --change-set-name {{ change_set_name }} \
    --region {{ region }}
```

Change Set が存在する場合の結果例:
```output
{
    "ChangeSetName": "{{ change_set_name }}",
    "StackName": "{{ stack_name }}",
    "Status": "CREATE_COMPLETE",
    "ExecutionStatus": "AVAILABLE",
    "Changes": [
        {
            "Type": "Resource",
            "ResourceChange": {
                "Action": "Modify",
                "LogicalResourceId": "TrainingBucket",
                "ResourceType": "AWS::S3::Bucket",
                "Replacement": "False",
                "Details": [
                    {
                        "Target": {
                            "Attribute": "Tags",
                            "RequiresRecreation": "Never"
                        },
                        "Evaluation": "Static",
                        "ChangeSource": "ParameterReference"
                    }
                ]
            }
        }
    ],
{% if stack_parameters %}
    "Parameters": [
{% for p in stack_parameters %}
        {
            "ParameterKey": "{{ p.key }}",
            "ParameterValue": "{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}"
        }{{ ',' if not loop.last else '' }}
{% endfor %}
    ]
{% else %}
    "Parameters": []
{% endif %}
}
```

Change Set が存在しない場合の結果例:
```output
An error occurred (ChangeSetNotFoundException) when calling the DescribeChangeSet operation: ChangeSet [{{ change_set_name }}] does not exist
```
