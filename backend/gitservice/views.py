import tempfile
import subprocess
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CopyGitHubRepoView(APIView):
    
    def post(self, request):
        try:
            source_repo = request.data.get("source_repo")
            source_token = request.data.get("source_token")
            target_repo = request.data.get("target_repo")
            target_owner = request.data.get("target_owner")
            target_token = request.data.get("target_token")

            if not all([source_repo, source_token, target_repo, target_owner, target_token]):
                return Response({"error": "All fields are required"},
                                status=status.HTTP_400_BAD_REQUEST)

            api_url = "https://api.github.com/user/repos"
            headers = {"Authorization": f"token {target_token}"}
            data = {"name": target_repo, "private": True}

            response = requests.post(api_url, json=data, headers=headers)
            if response.status_code not in [201, 422]:
                return Response({"error": f"Failed to create target repo: {response.text}"},
                                status=status.HTTP_400_BAD_REQUEST)

            target_repo_url = f"https://{target_token}@github.com/{target_owner}/{target_repo}.git"

            with tempfile.TemporaryDirectory() as tmpdir:
                src_repo_with_auth = source_repo.replace("https://", f"https://{source_token}@")

                subprocess.run(["git", "clone", "--mirror", src_repo_with_auth, tmpdir],
                               check=True)

                subprocess.run(["git", "--git-dir", tmpdir, "push", "--mirror", target_repo_url],
                               check=True)

            return Response({"message": "Repo copied successfully!",
                             "target_repo_url": target_repo_url},
                            status=status.HTTP_200_OK)

        except subprocess.CalledProcessError as e:
            return Response({"error": f"Git command failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
