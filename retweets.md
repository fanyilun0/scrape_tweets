好的，这是一个非常棒的优化点。监控白名单用户的转推，可以帮助我们发现他们认为有价值的内容，从而捕获到更多潜在的信息。

要实现这个功能，我们需要分两步走：

1.  **识别并抓取转推信息**：修改现有的抓取逻辑，使其能够分辨出一条推文是原创还是转推，并能同时提取出“转推者”和“原作者”的信息。
2.  **优化推送内容的格式**：设计一种新的消息格式，在推送时能清晰地展示这是一条转推，并突出“谁转推了谁的内容”。

-----

### 实现思路

在Twitter/X的页面结构中，一条转推（Retweet）通常包含两个部分：

1.  **社交上下文 (Social Context)**：在推文顶部会有一小行文字，如“`[白名单用户] Retweeted`”。这部分告诉我们是谁执行了“转推”这个动作。
2.  **原始推文 (Original Tweet)**：下面嵌入了被转发的完整推文内容，包括原作者、正文、图片等。

我们的核心思路就是：**在遍历每条推文时，首先检查是否存在“社交上下文”，如果存在，就判断执行转推的用户是否在我们的白名单里。**

**具体步骤：**

1.  **修改 `extract_tweet_data` 函数**：

      * 增加一个逻辑来检测推文 `article` 元素中是否存在表明“转推”的特定元素。
      * 如果检测到是转推：
          * 从“社交上下文”中提取**转推者**的用户名 (`retweeter_handle`)。
          * 将被嵌入的**原始推文**视为主要内容，从中提取原作者、正文、图片等信息。
          * 返回一个特殊的数据结构，比如增加一个字段 `is_retweet: True`，并同时包含 `retweeter` 和 `original_author` 的信息。
      * 如果不是转推，则按原逻辑处理。

2.  **修改 `is_user_in_whitelist` 的使用方式**：

      * 现在我们需要检查两种情况：
          * 对于原创推文，检查**作者**是否在白名单。
          * 对于转推，检查**转推者**是否在白名单。
      * 这个检查逻辑最好直接整合进 `extract_tweet_data` 函数，这样该函数返回的数据就都是我们想要的了。

3.  **修改 `send_tweet_to_webhook` 函数**：

      * 在函数内部，通过检查 `tweet_data.get('is_retweet')` 字段来判断推文类型。
      * 如果是转推，就使用新的、优化过的消息模板来组织推送内容。
      * 如果是原创，沿用旧的模板。

-----

### 代码调整实现

以下是具体的代码修改建议，您可以将其应用到您现有的脚本中。

#### 1\. 优化 `extract_tweet_data` 函数

这是最核心的修改。我们需要让这个函数变得更智能，能识别转推并提取所有需要的信息。

```python
def extract_tweet_data(tweet_article):
    """
    从推文元素中提取数据，能够区分原创和转推
    
    Args:
        tweet_article: Selenium WebElement，推文的article元素
        
    Returns:
        dict: 包含推文数据的字典，如果是不需要关注的推文则返回None
    """
    try:
        is_retweet = False
        retweeter_handle_raw = ""
        retweeter_display_name = ""

        # --- 新增：检测是否为转推 ---
        try:
            # 转推的上下文通常在这个testid的div里
            social_context = tweet_article.find_element(By.XPATH, ".//div[@data-testid='socialContext']")
            if "Retweeted" in social_context.text or "转推了" in social_context.text:
                is_retweet = True
                # 提取转推者的用户名
                retweeter_link = social_context.find_element(By.TAG_NAME, "a")
                retweeter_handle_raw = retweeter_link.get_attribute('href').split('/')[-1]
                retweeter_display_name = social_context.text.replace("Retweeted", "").strip()
        except NoSuchElementException:
            # 找不到socialContext，说明是原创推文
            is_retweet = False

        # 提取推文正文、用户名等核心信息（无论是原创还是转推，这部分结构是相似的）
        # ... (这里沿用您原函数大部分的提取逻辑) ...
        # ... 为了简洁，下面只列出关键部分的提取 ...

        # 提取用户名和显示名称 (这部分提取到的是原作者)
        user_handle_raw = ""
        user_display_name = ""
        try:
            user_name_div = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
            user_handle_raw = user_name_div.find_element(By.XPATH, ".//a[contains(@href, '/')]").get_attribute('href').split('/')[-1]
            user_display_name = user_name_div.find_element(By.XPATH, ".//span[contains(@class, 'css-1jxf684')]").text
        except NoSuchElementException:
            pass # 提取失败则为空

        # --- 新增：白名单过滤逻辑 ---
        # 如果是转推，我们关心的是转推者是否在白名单
        if is_retweet:
            if not is_user_in_whitelist(retweeter_handle_raw):
                # print(f"  ⊘ 跳过转推（转推者 {retweeter_handle_raw} 不在白名单）")
                return None # 直接返回None，跳过这条推文
        # 如果是原创，我们关心的是作者是否在白名单
        else:
            if not is_user_in_whitelist(user_handle_raw):
                # print(f"  ⊘ 跳过原创推文（作者 {user_handle_raw} 不在白名单）")
                return None # 直接返回None，跳过这条推文

        # 只有通过白名单检查的推文才会继续执行下面的提取逻辑
        # ... (继续执行您原有的 tweet_id, url, text, images, time 的提取逻辑) ...
        # (以下为示例)
        tweet_url = None
        tweet_id = None
        tweet_link_elements = tweet_article.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
        for link in tweet_link_elements:
            href = link.get_attribute('href')
            if '/status/' in href and 'analytics' not in href:
                tweet_url = href
                tweet_id = href.split('/status/')[-1].split('?')[0]
                break
        
        if not tweet_id: return None

        tweet_text = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text if tweet_article.find_elements(By.XPATH, ".//div[@data-testid='tweetText']") else ""
        tweet_time_str = tweet_article.find_element(By.TAG_NAME, "time").get_attribute('datetime') if tweet_article.find_elements(By.TAG_NAME, "time") else ""
        
        image_urls = []
        photo_divs = tweet_article.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']")
        for photo_div in photo_divs:
            img_elements = photo_div.find_elements(By.TAG_NAME, "img")
            for img_element in img_elements:
                img_url = img_element.get_attribute('src')
                if img_url and 'name=' in img_url:
                    image_urls.append(re.sub(r'name=\w+', 'name=orig', img_url))

        return {
            "id": tweet_id,
            "url": tweet_url,
            "is_retweet": is_retweet,
            "retweeter": { # 转推者信息
                "handle_raw": retweeter_handle_raw,
                "display_name": retweeter_display_name
            },
            "original_author": { # 原作者信息
                "handle_raw": user_handle_raw,
                "display_name": user_display_name
            },
            "time": datetime.fromisoformat(tweet_time_str.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if tweet_time_str else "",
            "text": tweet_text,
            "images": image_urls
        }
    except Exception as e:
        # print(f"  × 提取推文数据失败: {e}") # 调试时可以打开
        return None
```

#### 2\. 简化 `scrape_list_tweets` 函数

因为过滤逻辑已经移入了 `extract_tweet_data`，这里的循环可以简化。

```python
# scrape_list_tweets 函数中的循环部分可以修改为：

for article in tweet_articles:
    if len(tweets_data) >= max_tweets:
        break
    
    # extract_tweet_data现在会返回None如果推文不符合白名单要求
    tweet_data = extract_tweet_data(article) 
    
    if tweet_data and tweet_data['id'] not in processed_ids:
        processed_ids.add(tweet_data['id'])
        tweets_data.append(tweet_data)
        if tweet_data['is_retweet']:
            print(f"  ✓ 提取转推: {tweet_data['retweeter']['handle_raw']} RT @{tweet_data['original_author']['handle_raw']}")
        else:
            print(f"  ✓ 提取原创: @{tweet_data['original_author']['handle_raw']}")

# ... 后续滚动逻辑中的循环也做类似修改 ...
```

#### 3\. 优化 `send_tweet_to_webhook` 函数（优化推送内容）

这是向用户展示最终成果的部分。我们需要为转推设计一个清晰的格式。

```python
async def send_tweet_to_webhook(tweet_data):
    """将推文数据发送到webhook，为转推提供专门格式"""
    try:
        message_parts = []
        
        # --- 根据是否为转推，生成不同格式的消息 ---
        if tweet_data.get('is_retweet'):
            # 这是转推
            message_parts.append(f"🔄 **用户转推提醒**")
            retweeter = tweet_data['retweeter']
            original_author = tweet_data['original_author']
            
            # 突出转推者
            message_parts.append(f"👤 **转推者**: {retweeter['display_name']} (@{retweeter['handle_raw']})")
            # 标明原作者
            message_parts.append(f"✍️ **原作者**: {original_author['display_name']} (@{original_author['handle_raw']})")
        else:
            # 这是原创推文
            message_parts.append(f"🐦 **新推文监听**")
            author = tweet_data['original_author'] # 对于原创，original_author就是作者
            message_parts.append(f"👤 **作者**: {author['display_name']} (@{author['handle_raw']})")

        if tweet_data['time']:
            message_parts.append(f"🕐 **时间**: {tweet_data['time']}")
        
        message_parts.append("")
        
        if tweet_data['text']:
            message_parts.append(f"📝 **内容**:")
            message_parts.append(tweet_data['text'])
            message_parts.append("")
            
        if tweet_data['url']:
            message_parts.append(f"🔗 **链接**: {tweet_data['url']}")
            
        if tweet_data['images']:
            message_parts.append(f"🖼️ 包含 {len(tweet_data['images'])} 张图片")
            
        message = "\n".join(message_parts)
        print(f"  准备发送通知...")
        await send_message_async(message, msg_type="text")
        
        # ... 后续发送图片的逻辑保持不变 ...
        
        print(f"✓ 推文推送完成: {tweet_data['id']}")
        return True
        
    except Exception as e:
        print(f"× 推送推文失败: {e}")
        return False
```

### 总结

通过以上三步修改，您的脚本现在就具备了监控白名单用户转推的能力。

  * **推送效果预览（转推）**:

    ```
    🔄 用户转推提醒
    👤 转推者: some_KOL (@some_KOL_handle)
    ✍️ 原作者: Original Author (@original_author_handle)
    🕐 时间: 2025-10-08 15:30:00

    📝 内容:
    This is the content of the original tweet that was retweeted.

    🔗 链接: https://x.com/original_author_handle/status/123456789
    🖼️ 包含 1 张图片
    ```

  * **推送效果预览（原创）**:

    ```
    🐦 新推文监听
    👤 作者: some_KOL (@some_KOL_handle)
    🕐 时间: 2025-10-08 15:35:00

    📝 内容:
    This is an original tweet from the whitelisted user.

    🔗 链接: https://x.com/some_KOL_handle/status/987654321
    ```

这样的格式既能清晰地区分事件类型，又能完整地提供上下文信息，大大提升了监控脚本的价值。