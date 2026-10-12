# 12-Factor Config Precedence API

## Deploy on Render
1. Upload this folder to a GitHub repository.
2. In Render, choose **New + → Blueprint** and connect the repository containing `render.yaml`.
3. Deploy the service. Render will provide a public HTTPS URL.
4. Open `https://YOUR-SERVICE.onrender.com/effective-config`.
5. Submit that URL in the assignment.

Test overrides:
`https://YOUR-SERVICE.onrender.com/effective-config?set=port=9000&set=debug=true`

The response always masks `api_key` as `****`. The `set` query parameter can be repeated.
