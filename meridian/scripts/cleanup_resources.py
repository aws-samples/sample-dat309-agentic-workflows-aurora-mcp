"""
Cleanup remaining AWS resources for Meridian demo.
Deletes secrets, subnet groups, and security groups.
"""
import boto3
from rich.console import Console

console = Console()


def cleanup_resources(region: str = "us-east-1"):
    """Clean up remaining Meridian resources in the specified region."""
    console.print(f"\n[bold blue]🧹 Cleaning up resources in {region}[/bold blue]\n")
    
    # Initialize clients
    secretsmanager = boto3.client("secretsmanager", region_name=region)
    rds = boto3.client("rds", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)
    
    # Delete secret
    console.print("[yellow]Deleting Secrets Manager secret...[/yellow]")
    try:
        secretsmanager.delete_secret(
            SecretId="meridian-demo-credentials",
            ForceDeleteWithoutRecovery=True
        )
        console.print("[green]✅ Secret deleted[/green]")
    except secretsmanager.exceptions.ResourceNotFoundException:
        console.print("[dim]Secret already deleted or not found[/dim]")
    except Exception as e:
        console.print(f"[red]Error deleting secret: {e}[/red]")
    
    # Delete subnet group
    console.print("[yellow]Deleting DB subnet group...[/yellow]")
    try:
        rds.delete_db_subnet_group(DBSubnetGroupName="meridian-demo-subnet-group")
        console.print("[green]✅ Subnet group deleted[/green]")
    except rds.exceptions.DBSubnetGroupNotFoundFault:
        console.print("[dim]Subnet group already deleted or not found[/dim]")
    except Exception as e:
        console.print(f"[red]Error deleting subnet group: {e}[/red]")
    
    # Delete security group
    console.print("[yellow]Deleting security group...[/yellow]")
    try:
        response = ec2.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": ["meridian-demo-sg"]}]
        )
        if response["SecurityGroups"]:
            sg_id = response["SecurityGroups"][0]["GroupId"]
            ec2.delete_security_group(GroupId=sg_id)
            console.print(f"[green]✅ Security group {sg_id} deleted[/green]")
        else:
            console.print("[dim]Security group already deleted or not found[/dim]")
    except Exception as e:
        console.print(f"[red]Error deleting security group: {e}[/red]")
    
    console.print(f"\n[green]✅ Cleanup complete for {region}![/green]\n")


if __name__ == "__main__":
    cleanup_resources("us-east-1")
