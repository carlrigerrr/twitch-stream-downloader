# Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No playable streams found" Error

**Symptom:**
```
ERROR - Video not available: [Video Title]
ERROR - Reason: No playable streams (subscriber-only, deleted, or geo-restricted)
```

**Why This Happens:**
The Twitch API returns videos in search results, but many of them cannot be downloaded because they are:
- **Subscriber-only content** - Requires a Twitch subscription to view
- **Deleted/expired videos** - No longer available on Twitch
- **Geo-restricted** - Not available in your region
- **Authenticated-only** - Requires being logged into Twitch

**Solutions:**

#### Solution 1: Try Different Videos (Easiest)
1. Fetch more videos by increasing "Max Videos" filter (e.g., 50-100)
2. The app will check each video and skip unavailable ones
3. Look for videos from popular streamers (they're usually public)

#### Solution 2: Look for Public Videos
Try categories with more public content:
- Just Chatting
- Popular games (Minecraft, Fortnite, League of Legends)
- Esports events
- Official game streams

#### Solution 3: Use Less Restrictive Filters
- Reduce minimum view count
- Increase duration range
- Try "all" for video type instead of specific types
- Increase "Days Back" to get more results

#### Solution 4: Check Individual Videos Manually
Before downloading, you can verify a video is publicly available:
1. Copy the video URL from Twitch
2. Try opening it in an incognito/private browser window
3. If it plays without login, it should be downloadable

---

### Issue: All Downloaded Videos Fail

**Symptoms:**
- Multiple videos fail to download
- Log shows "No playable streams" for all videos

**Possible Causes & Solutions:**

#### 1. Category Has Mostly Subscriber Content
**Solution:** Try a different game category with more public streams

#### 2. Regional Restrictions
**Solution:**
- Use a VPN to a different region
- Try videos from international streamers

#### 3. Streamlink Needs Update
**Solution:**
```bash
pip install --upgrade streamlink
```

---

### Issue: Some Videos Download, Others Don't

**This is Normal!**
- Not all videos on Twitch are publicly downloadable
- The app now checks each video before downloading
- Failed videos will show specific error reasons in logs

**What to Do:**
1. Check the logs to see why specific videos failed
2. Increase "Max Videos" to get more options
3. Select only the videos that passed the availability check

---

### Issue: Slow Video Fetching

**Symptom:** Takes a long time to fetch videos

**Why:** The app checks availability of each video

**Solutions:**
1. Reduce "Max Videos" count if you don't need many
2. Use more specific filters to reduce total videos checked
3. Be patient - checking 100+ videos can take 2-3 minutes

---

### Issue: No Videos Match Filters

**Symptom:**
```
No videos match your filter criteria after checking X videos
```

**Solutions:**
1. **Relax duration filters** - Remove min/max duration temporarily
2. **Lower view count requirements** - Try min views: 1000 instead of 10000
3. **Increase days back** - Try 14 or 30 days instead of 7
4. **Change video type** - Try "all" instead of specific type
5. **Try different category** - Some categories have more videos

---

## Best Practices

### For Best Success Rate:

1. **Start with loose filters:**
   ```
   Days Back: 7
   Max Videos: 50
   Language: all
   Type: all
   (no duration or view filters)
   ```

2. **Gradually add filters:**
   - After you see results, add duration range
   - Then add minimum views
   - Finally, restrict language/type

3. **Use popular categories:**
   - Categories with 10K+ viewers typically have more public content
   - Smaller categories often have more subscriber-only content

4. **Expect some failures:**
   - It's normal for 20-40% of videos to be unavailable
   - Focus on the successful downloads

---

## Understanding Video Availability

### Why Twitch API Shows Videos That Can't Be Downloaded:

The Twitch API returns **all** videos in search results, including:
- ✅ Public videos (downloadable)
- ❌ Subscriber-only videos (not downloadable without subscription)
- ❌ Deleted videos (not downloadable)
- ❌ Geo-restricted videos (not downloadable in your region)

**This is by design** - Twitch's API doesn't filter by download availability.

### The App's Behavior:

1. **Fetches** videos from Twitch API
2. **Filters** them by your criteria (duration, views, etc.)
3. **Checks** each video for availability before downloading
4. **Downloads** only available videos
5. **Reports** specific errors for failed videos

---

## Checking Logs

To see detailed error information:

1. **Console Output:**
   - Run `python main.py` from terminal
   - Watch for ERROR messages during downloads

2. **Log Files:**
   - Check `logs/twitch_downloader_YYYYMMDD.log`
   - Search for "ERROR" to find issues
   - Look for specific video titles

3. **Understanding Log Messages:**
   ```
   INFO - Checking video availability: [Title]
   ERROR - Video not available: [Title]
   ERROR - Reason: No playable streams (subscriber-only, deleted, or geo-restricted)
   ```

---

## When to Report Issues

**Don't Report:**
- Individual videos failing (this is expected)
- "No playable streams" errors (videos are subscriber-only)

**Do Report:**
- App crashes
- All videos failing in multiple categories
- Unexpected errors or bugs
- UI problems

---

## Advanced: Testing Video Availability

To manually test if a video is downloadable:

```bash
# List available streams for a video
streamlink https://www.twitch.tv/videos/VIDEO_ID

# If you see "Available streams:", the video is downloadable
# If you see "No playable streams", it's not downloadable
```

---

## FAQ

**Q: Why can't I download all videos I see on Twitch?**
A: Many videos are subscriber-only or require authentication. The app can only download publicly available videos.

**Q: Can I download subscriber-only content if I have a subscription?**
A: Currently no - adding Twitch authentication is a planned feature.

**Q: Why does fetching take so long?**
A: The app checks each video for availability, which takes time. More videos = more time.

**Q: How can I increase success rate?**
A: Use popular categories, increase "Max Videos" count, and use loose filters initially.

**Q: Some videos play on Twitch but won't download. Why?**
A: You might be logged into Twitch in your browser. Try the video in incognito mode - if it doesn't play, it's not publicly available.

---

## Need More Help?

1. Check the main README.md for setup instructions
2. Run `python test_download.py` to test your setup
3. Check logs in `logs/` folder
4. Create an issue on GitHub with:
   - Error message from logs
   - Category you're trying to download from
   - Filter settings you used
