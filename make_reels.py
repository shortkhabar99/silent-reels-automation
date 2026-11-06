
name: Instagram Reel Automation

on:
  workflow_dispatch:
  schedule:
    - cron: '*/30 * * * *'

permissions:
  contents: write

concurrency:
  group: instagram-reel-automation
  cancel-in-progress: false

jobs:
  publish-reels:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install fonts
        run: |
          sudo apt-get update
          sudo apt-get install -y fonts-noto-core

      - name: Install packages
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install cloudinary

      - name: Update news
        run: python main.py

      - name: Generate reels if queue is empty
        run: |
          python -c "import os,glob,json,sys; s=json.load(open('publish_state.json')) if os.path.exists('publish_state.json') else {'published': []}; files=glob.glob('reels/*.mp4'); sys.exit(0 if any(f not in s.get('published',[]) for f in files) else 1)" || python make_reels.py

      - name: Verify reels
        run: |
          python -c "import glob,sys; f=glob.glob('reels/*.mp4'); print('Available reels:',len(f)); sys.exit(0 if f else 1)"

      - name: Publish Instagram Reel
        env:
          CLOUDINARY_URL: ${{ secrets.CLOUDINARY_URL }}
          INSTAGRAM_ACCOUNT_ID: ${{ secrets.INSTAGRAM_ACCOUNT_ID }}
          PAGE_ACCESS_TOKEN: ${{ secrets.PAGE_ACCESS_TOKEN }}
        run: python publish_instagram.py

      - name: Save automation data
        run: |
          git config user.name "News Bot"
          git config user.email "news-bot@users.noreply.github.com"
          git add -A
          git diff --cached --quiet || git commit -m "Update Instagram reel automation"
          git push
