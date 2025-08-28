
# AssetOpsBench Setup Guide

This guide describes how to fork, configure, and run the **AssetOpsBench** project using Conda and Docker on macOS.

---

## Fork to Your Own Project

This guide shows how to create your own copy of the **IBM/AssetOpsBench** project on GitHub, using only the web browser.  
A fork lets you experiment and make changes without affecting the original project.

---

### Step 1 — Log in to GitHub
1. Open [https://github.com](https://github.com) in your browser.  
2. Sign in with your GitHub account.  
   - If you don’t have one, click **Sign up** to create a free account.

---

### Step 2 — Navigate to the Original Repository
1. In the search bar at the top of GitHub, type **IBM/AssetOpsBench**.  
2. Click on the repository link, or go directly to:  
   👉 [https://github.com/IBM/AssetOpsBench](https://github.com/IBM/AssetOpsBench)

---

### Step 3 — Required Branch for This Work
The repository contains multiple branches, but for this purpose you will only use:

- **`Competition_CODS`** → this branch contains the competition-specific code and materials.  

👉 You still need to fork with **all branches** available so you can access `Competition_CODS`.

---

### Step 4 — Create the Fork
1. On the top-right of the page, click the **Fork** button.  
   ![fork-button](https://docs.github.com/assets/cb-30686/images/help/repository/fork_button.png)  

2. On the fork setup page:  
   - Make sure your own GitHub account is selected as the destination.  
   - **Important:** Uncheck the option **“Copy the `main` branch only.”**  
     - Leaving it checked will copy only `main`.  
     - Unchecking ensures you also get **`Competition_CODS`** and other branches.  

3. Click **Create fork**.

---

### Step 5 — Switch to the `Competition_CODS` Branch
1. Go to your forked repository:  
   👉 `https://github.com/<your-username>/AssetOpsBench`

2. Open the **Branch dropdown menu** (upper-left, just above the file list).  
   ![branch-dropdown](https://docs.github.com/assets/cb-33248/images/help/branch/branch-dropdown.png)

3. Select **`Competition_CODS`** from the list.  
   - This switches your forked repository view to the competition branch.  

---

### Step 6 — Verify Your Fork
- After switching, confirm that the branch name `Competition_CODS` is shown at the top-left of the repository.  
- All further work for the competition should be done in this branch.

---

### Important Notes
- Always uncheck **“Copy the `main` branch only”** when forking. Otherwise you won’t see `Competition_CODS`.  
- Even though other branches are copied, you only need to use **`Competition_CODS`** for this competition.


## 2. Clone to Your Local Machine (Using GitHub Desktop)

Once you have forked the repository on GitHub, you may want to work with it locally on your computer.  
Here we use **GitHub Desktop** to illustrate the process.

---

### Step 1 — Install GitHub Desktop
1. Download GitHub Desktop from: https://desktop.github.com  
2. Install and open the application.  
3. Sign in with your GitHub account.

---

### Step 2 — Locate Your Fork
1. In your browser, go to your forked repository:  
   `https://github.com/<your-username>/AssetOpsBench`
2. Click the green **Code** button.  
3. Select **Open with GitHub Desktop**.  
   - This will launch GitHub Desktop and prepare to clone your fork.

---

### Step 3 — Choose the Local Path
1. In GitHub Desktop, choose where to save the project locally.  
2. Set the path to:
	local path:  <your_local_directory>/codabench/AssetOpsBench
	

### Step 4 — Switch to the `Competition_CODS` Branch
⚠️ For this competition, you must work **only** on the `Competition_CODS` branch.

1. In GitHub Desktop, use the **Current Branch** dropdown (top bar).  
2. Select `Competition_CODS` from the list.  
   - If you don’t see it, ensure you unchecked “Copy the main branch only” when you forked.

---

### Step 5 — Verify
1. The branch name shown at the top of GitHub Desktop should be **Competition_CODS**.  
2. Confirm the file view matches the content of this branch.

---

✅ You have successfully cloned your fork locally with GitHub Desktop and switched to the **`Competition_CODS`** branch. All further work should be done in this branch.




## 3. Docker Setup (Rancher Desktop)

We use **Rancher Desktop** for the Docker CLI and engine. Install it from [https://rancherdesktop.io](https://rancherdesktop.io).

### 3.1 Install & Configure
1. Open **Rancher Desktop** → **Preferences**.  
2. Go to **Virtual Machine → Emulation**:  
   - **Virtual Machine Type**:  
     - `VZ` (recommended on Apple Silicon) → uses the Apple Virtualization framework.  
     - `QEMU` → software emulator (slower, only if VZ is unavailable).  
   - **VZ Option**: enable **Rosetta support** to run amd64 (x86) Docker images on Apple Silicon.  
3. Click **Apply**. Rancher Desktop will restart with the new settings.

### 3.2 (Optional) Verify the Docker CLI
You can check that the `docker` command is coming from Rancher Desktop.

```bash
which docker
docker version
```

**Expected path (example):**
```
~/.rd/bin/docker
```

- On macOS this expands to `/Users/<your-username>/.rd/bin/docker`.  
- On Linux it expands to `/home/<your-username>/.rd/bin/docker`.  

If you see `/usr/local/bin/docker`, another Docker runtime (e.g., Docker Desktop) is active. Quit it and ensure Rancher Desktop is running.

### 3.3 (If Kubernetes is On) Ensure Certificates Are Fresh
If you enable Kubernetes in Rancher Desktop, its certificates can expire and block startup.

**Quick checks:**
```bash
kubectl version --short
kubectl get nodes
kubectl cluster-info
```

**If errors mention expired or invalid certificates:**
- In Rancher Desktop: go to **Preferences → Kubernetes → Reset Kubernetes** (regenerates certificates).  
- If problems persist: use **Preferences → Troubleshooting → Factory Reset** (removes images/containers and resets certificates).

---

## 4. Build and Run

Follow the official **benchmark README**:  
https://github.com/IBM/AssetOpsBench/blob/main/benchmark/README.md

## 5. Environment Variables

Fill in your `.env` file with the following:

```env
COUCHDB_USERNAME=admin
COUCHDB_PASSWORD=password
COUCHDB_DBNAME=chiller
COUCHDB_URL=http://couchdb:5984/

WATSONX_APIKEY=
WATSONX_PROJECT_ID=
WATSONX_URL=

PATH_TO_DATASETS_DIR=/opt/conda/envs/assetopsbench/lib/python3.12/site-packages/tsfmagent/data/datasets
PATH_TO_MODELS_DIR=/opt/conda/envs/assetopsbench/lib/python3.12/site-packages/tsfmagent/data/tsfm_models
PATH_TO_OUTPUTS_DIR=/opt/conda/envs/assetopsbench/lib/python3.12/site-packages/tsfmagent/output

SKYSPARK_USERNAME=
SKYSPARK_PASSWORD=
SKYSPARK_URL=

OPENAI_API_KEY=
```

### Notes
- **Skyspark credentials**: Required but cal leave empty
- **OpenAI API key**: Required but should leave as empty

---

## 6. References

- [AssetOpsBench GitHub](https://github.com/IBM/AssetOpsBench)
- [Benchmark README](https://github.com/IBM/AssetOpsBench/blob/main/benchmark/README.md)
- [Rancher Desktop](https://rancherdesktop.io/)
- [Docker Hub](https://hub.docker.com/)
- [Quay.io](https://quay.io/) (Red Hat container registry)

