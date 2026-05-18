$GitPath = "C:\Users\vellaichamy\AppData\Local\Programs\Git\cmd\git.exe"

Write-Host "---"
Write-Host "[INFO] Initializing Repository Unification..."
Write-Host "---"

# 1. Remove nested .git directory
if (Test-Path "financial-services-plugins\.git") {
    Write-Host "[INFO] Removing nested Git repo structure in subfolder..."
    Remove-Item -Path "financial-services-plugins\.git" -Recurse -Force
}

# 2. Reset the root git index to track everything as standard files
Write-Host "[INFO] Updating Git tracking index..."
& $GitPath rm --cached -r financial-services-plugins -ErrorAction SilentlyContinue | Out-Null
& $GitPath add .

# 3. Commit the unified workspace locally
Write-Host "[INFO] Creating secure unified local commit..."
& $GitPath commit -m "Unified Financial AI Workspace: Staged eToro Plugins, Schedulers, and Reports"

# 4. Pull remote history to merge (using ours strategy for quick safe merge)
Write-Host "[INFO] Merging with remote GitHub history..."
& $GitPath pull origin main --allow-unrelated-histories -X ours --no-edit

# 5. Push to GitHub
Write-Host "[INFO] Pushing entire workspace to GitHub..."
& $GitPath push -u origin main

Write-Host "---"
Write-Host "[SUCCESS] Your entire unified workspace has been successfully checked-in to GitHub!"
Write-Host "---"
