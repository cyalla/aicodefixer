from flask import Blueprint, jsonify, request
import json 
import requests

github_bp = Blueprint('createGithubIssue', __name__)

@github_bp.route('/createGithubIssue', methods=['POST'])
def create_github_issue():
    #TO DO - To modify it for general repo
    repo_owner = 'cyalla'
    repo_name = 'productrepo'
    token = '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'

    data = request.json
    title = data.get("title")
    body = data.get("body")

    if not title or not body:
        return jsonify({'error': 'Title and body are required'}), 400

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    payload = {
        'title': title,
        'body': body
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        issue_id = response.json()['number']
        return jsonify({'IssueId': issue_id}), 201
    else:
        error_message = f"Failed to create GitHub issue: {response.status_code} - {response.text}"
        app.logger.error(error_message)  # Log the error
        return jsonify({'error': error_message}), 500