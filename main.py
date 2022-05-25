import boto3
import csv


def convert_to_string(input_list):
	delimiter = ','
	out_string = delimiter.join(input_list)
	return out_string


def get_iam_users(iam_client):
	iam_users = []
	paginator = iam_client.get_paginator("list_users")
	page_iterator = paginator.paginate()
	for page in page_iterator:
		for each_user in page['Users']:
			iam_users.append(each_user['UserName'])
	return iam_users

def get_iam_groups(iam_client,username):
	group_list = []
	groups = ''
	group_response = iam_client.list_groups_for_user(UserName=username)['Groups']
	for each_group in group_response:
		group_list.append(each_group['GroupName'])
		groups = convert_to_string(group_list)
	return groups

def get_managed_policies(iam_client,username):
	managed_policies = []
	response = iam_client.list_attached_user_policies(UserName=username)['AttachedPolicies']
	for each_policy in response:
		managed_policies.append(each_policy['PolicyName'])
	# print(managed_policies)
	return managed_policies

def get_inline_policies(iam_client,username):
	inline_policies = []
	inline_policies = iam_client.list_user_policies(UserName=username)['PolicyNames']
	# print(inline_policies)
	return inline_policies


def get_iam_policies(iam_client,username):
	iam_policies_list = []
	managed_policy_list = get_managed_policies(iam_client,username)
	inline_policy_list = get_inline_policies(iam_client,username)
	iam_policies_list = managed_policy_list + inline_policy_list
	policies = convert_to_string(iam_policies_list)
	return policies

def check_mfa(iam_client,username):
	mfa_check_list = []
	mfa_resp = iam_client.list_mfa_devices(UserName=username)
	if len(mfa_resp['MFADevices']) != 0:
		mfa_check_list.append('Enabled')
	else:
		mfa_check_list.append('Disabled')
	mfa_check = convert_to_string(mfa_check_list)
	return mfa_check


def main():
	iam_details = []
	client = boto3.client('iam')
	users_list = get_iam_users(client)
	print("Printing the IAM Users List")
	print(users_list)
	for user in users_list:
		iam_groups  = get_iam_groups(client,user)
		iam_policies = get_iam_policies(client,user)
		mfa_status = check_mfa(client,user)
		iam_details.append({'IAMUserName' : user, 'IAMGroups' : iam_groups, 'IAMPolicies' : iam_policies, 'MFA' : mfa_status})
	print(iam_details)
	header = ['IAMUserName', 'IAMGroups', 'IAMPolicies', 'MFA']
	with open('iam-details.csv', 'w') as file:
		writer = csv.DictWriter(file, fieldnames=header)
		writer.writeheader()
		writer.writerows(iam_details)
	

if __name__ == '__main__':
    main()
