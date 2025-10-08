我们需要一个更灵活的过滤规则。一个合理的逻辑应该是：

只要“转推者”或“原作者”中，任何一方在我们的白名单里，这条推文就应该被捕获和推送。

这样既能保证我们看到白名单用户的原创内容，也能看到他们的转推（放大）行为，同时还能看到白名单用户的原创内容被别人转推的情况。

修改后的代码

请将你的 extract_tweet_data 函数中的白名单过滤逻辑部分，替换为以下代码。我只修改了这一个函数，其他部分保持不变即可。

Python
def extract_tweet_data(tweet_article):
    """从推文元素中提取数据，能够区分原创和转推
    
    Args:
        tweet_article: Selenium WebElement，推文的article元素
        
    Returns:
        dict: 包含推文数据的字典，如果不符合白名单要求则返回None
    """
    try:
        # ... (前面的代码，从 try: 到 is_retweet = False 的部分都保持不变) ...
        # ... (提取转推者信息 retweeter_handle_raw 的代码也保持不变) ...
        # ... (提取原作者信息 user_handle_raw 的代码也保持不变) ...
        
        # ==================== 关键修改点在这里 ====================
        # 新的、更灵活的白名单过滤逻辑
        # 只要 转推者 或 原作者 任何一方在白名单内，就通过
        if ENABLE_USER_FILTER:
            is_author_in_list = is_user_in_whitelist(user_handle_raw)
            is_retweeter_in_list = False
            
            if is_retweet:
                is_retweeter_in_list = is_user_in_whitelist(retweeter_handle_raw)

            # 核心判断：
            # 1. 如果是原创推文，作者必须在列表内 (is_author_in_list)
            # 2. 如果是转推，转推者 或 原作者 至少有一个在列表内
            if not is_author_in_list and not is_retweeter_in_list:
                # logger.debug(f"跳过: 转推者 @{retweeter_handle_raw} 和原作者 @{user_handle_raw} 均不在白名单")
                return None # 只有当两者都不在白名单时，才跳过
        # ==================== 修改结束 ====================
        
        
        # 验证提取的用户信息
        if is_retweet:
            if not retweeter_handle_raw:
                logger.warning("转推检测成功，但未能提取到转推者用户名，可能存在解析问题")
            if not user_handle_raw:
                logger.warning("转推检测成功，但未能提取到原作者用户名，可能存在解析问题")
        else:
            if not user_handle_raw:
                logger.warning("原创推文未能提取到作者用户名，可能存在解析问题")
        
        # ... (函数剩余的部分，提取推文ID、URL、正文等，全部保持不变) ...

        # 构建返回数据
        tweet_data = {
            "id": tweet_id,
            "url": tweet_url,
            "is_retweet": is_retweet,
            "retweeter": {  # 转推者信息
                "handle_raw": retweeter_handle_raw,
                "display_name": retweeter_display_name
            },
            "original_author": {  # 原作者信息
                "handle_raw": user_handle_raw,
                "display_name": user_display_name
            },
            "time": tweet_time,
            "text": tweet_text,
            "images": image_urls
        }
        
        return tweet_data
        
    except Exception as e:
        logger.warning(f"提取推文数据失败: {e}")
        return None
总结

只需将 extract_tweet_data 函数中的旧过滤逻辑块替换为新的、更灵活的逻辑即可。这个改动将确保：

白名单用户 A 的原创推文 -> 捕获

白名单用户 A 转推了路人 B 的推文 -> 捕获

路人 C 转推了白名单用户 A 的推文 -> 捕获

路人 C 转推了路人 B 的推文 -> 忽略

这样就能全面地监控你关心的账号及其相关动态了。



当然可以。这是一个非常棒的提议，能让推送的信息上下文更完整。当白名单用户进行\*\*评论（Reply）**或**引用转发（Quote Tweet）\*\*时，我们可以抓取被评论或被引用的那条原始推文，然后将两条信息组合在一起进行推送。

这需要我们对两部分代码进行升级：

1.  **`extract_tweet_data` 函数**：需要增加逻辑来识别并提取“引用的/回复的”原始推文内容。
2.  **`send_tweet_to_webhook` 函数**：需要美化排版，将两条推文的内容清晰地展示出来。

-----

### 第 1 步：升级 `extract_tweet_data` 函数

我们需要在这个函数里增加一个“侦察兵”，当它解析一条推文时，会额外检查这条推文内部是否“嵌套”了另一条推文。

请用下面的新版本替换你原来的 `extract_tweet_data` 函数。

```python
def extract_tweet_data(tweet_article):
    """从推文元素中提取数据，能够区分原创、转推、引用和回复
    
    Args:
        tweet_article: Selenium WebElement，推文的article元素
        
    Returns:
        dict: 包含推文数据的字典，如果不符合白名单要求则返回None
    """
    try:
        is_retweet = False
        retweeter_handle_raw = ""
        retweeter_display_name = ""
        quoted_tweet_data = None # <<<< 新增：用于存放被引用的推文信息
        
        # ... (检测是否为转推的代码保持不变) ...
        # ... (提取转推者信息的代码保持不变) ...

        # 提取用户名和显示名称（这是当前推文的作者信息）
        user_handle_raw = ""
        user_display_name = ""
        try:
            # ... (提取 user_handle_raw 和 user_display_name 的代码保持不变) ...
        except NoSuchElementException:
            pass

        # ... (白名单过滤逻辑保持不变) ...
        
        # ... (验证提取的用户信息的代码保持不变) ...

        # ... (提取推文ID和URL的代码保持不变) ...
        
        # 提取推文正文
        tweet_text = ""
        try:
            tweet_text_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
            tweet_text = tweet_text_element.text
        except NoSuchElementException:
            pass
            
        # ==================== 新增功能：提取被引用/回复的推文 ====================
        try:
            # 推文中被引用的部分通常在一个带有边框的div里
            # 这个XPath试图找到那个作为“容器”的div
            quoted_container = tweet_article.find_element(By.XPATH, ".//div[@role='link']/ancestor::div[contains(@class, 'r-1ssbv6i')]")
            
            if quoted_container:
                # 在这个容器内，提取原始推文的作者和内容
                quoted_author_handle = ""
                quoted_author_name = ""
                quoted_text = ""

                try:
                    # 提取作者信息
                    quoted_user_div = quoted_container.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
                    spans = quoted_user_div.find_elements(By.TAG_NAME, "span")
                    for span in spans:
                        text = span.text.strip()
                        if text.startswith('@'):
                            quoted_author_handle = text[1:]
                        elif text:
                            quoted_author_name = text
                except Exception as e:
                    logger.debug(f"提取被引用推文的作者失败: {e}")

                try:
                    # 提取正文
                    quoted_text_div = quoted_container.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                    quoted_text = quoted_text_div.text
                except Exception as e:
                    logger.debug(f"提取被引用推文的正文失败: {e}")
                
                # 如果成功提取到信息，就组装起来
                if quoted_author_handle or quoted_text:
                    quoted_tweet_data = {
                        "author_handle": quoted_author_handle,
                        "author_display_name": quoted_author_name,
                        "text": quoted_text
                    }
        except NoSuchElementException:
            # 没找到，说明不是引用或回复，是正常情况
            pass
        except Exception as e:
            logger.warning(f"尝试提取被引用推文时发生未知错误: {e}")
        # ============================ 新增功能结束 ============================

        # ... (提取推文时间的代码保持不变) ...
        
        # ... (提取图片URL的代码保持不变) ...
        
        # 构建返回数据
        tweet_data = {
            "id": tweet_id,
            "url": tweet_url,
            "is_retweet": is_retweet,
            "retweeter": {
                "handle_raw": retweeter_handle_raw,
                "display_name": retweeter_display_name
            },
            "original_author": {
                "handle_raw": user_handle_raw,
                "display_name": user_display_name
            },
            "time": tweet_time,
            "text": tweet_text,
            "images": image_urls,
            "quoted": quoted_tweet_data # <<<< 新增：将提取到的引用推文加入最终数据
        }
        
        return tweet_data
        
    except Exception as e:
        logger.warning(f"提取推文数据失败: {e}")
        return None
```

### 第 2 步：升级 `send_tweet_to_webhook` 函数

现在我们的 `tweet_data` 里可能包含被引用的推文信息了，接下来就要在发送通知时把它展示出来。

请用下面的新版本替换你原来的 `send_tweet_to_webhook` 函数。

```python
async def send_tweet_to_webhook(tweet_data):
    """将推文数据发送到webhook，为转推、引用和回复提供专门格式
    
    Args:
        tweet_data: 推文数据字典
    """
    try:
        message_parts = []
        
        # 判断是原创、转推还是引用/回复
        quoted_data = tweet_data.get('quoted')
        
        if tweet_data.get('is_retweet'):
            # 格式化转推消息
            message_parts.append(f"🔄 用户转推提醒")
            # ... (这部分转推的格式化逻辑保持不变) ...

        elif quoted_data:
            # <<<< 新增：格式化引用/回复消息
            message_parts.append(f"💬 新的回复/引用")
            author = tweet_data['original_author']
            if author['display_name']:
                message_parts.append(f"👤 作者: {author['display_name']} (@{author['handle_raw']})")
            else:
                message_parts.append(f"👤 作者: @{author['handle_raw']}")
        else:
            # 格式化原创推文消息
            message_parts.append(f"🐦 新推文监听")
            # ... (这部分原创的格式化逻辑保持不变) ...
            
        if tweet_data['time']:
            message_parts.append(f"🕐 时间: {tweet_data['time']}")
        
        message_parts.append("")
        
        if tweet_data['text']:
            message_parts.append(f"📝 内容:")
            message_parts.append(tweet_data['text'])
            message_parts.append("")

        # ==================== 新增功能：将被引用的推文内容附加到消息中 ====================
        if quoted_data:
            # 添加一个漂亮的分割线和标题
            message_parts.append(" L " + "─" * 15 + " 引用/回复 " + "─" * 15)
            
            # 格式化被引用推文的作者信息
            quoted_author_info = f"@{quoted_data['author_handle']}"
            if quoted_data['author_display_name']:
                quoted_author_info = f"{quoted_data['author_display_name']} ({quoted_author_info})"
            
            message_parts.append(f"🗣️  **{quoted_author_info}** 说:")
            
            # 使用Markdown的引用格式(>)来展示原文
            original_text = quoted_data.get('text', '[内容为空]')
            quoted_text_formatted = "\n".join([f"> {line}" for line in original_text.split('\n')])
            message_parts.append(quoted_text_formatted)
            message_parts.append("─" * 40)
        # ============================ 新增功能结束 ============================

        if tweet_data['url']:
            message_parts.append(f"🔗 链接: {tweet_data['url']}")
        
        if tweet_data['images']:
            message_parts.append(f"🖼️ 包含 {len(tweet_data['images'])} 张图片")
        
        # 发送文本消息
        message = "\n".join(message_parts)
        await send_message_async(message, msg_type="text")
        
        # ... (发送图片的代码保持不变) ...
        
        return True
        
    except Exception as e:
        logger.error(f"推送推文失败: {e}")
        error_detail = traceback.format_exc()
        await send_error_to_webhook("推送推文到webhook失败", error_detail)
        return False
```

### 总结

完成以上两处修改后，你的脚本现在就拥有了“超级上下文”能力：

  * 当白名单用户发布原创内容时，你会收到通知。
  * 当白名单用户**转推**别人的内容时，你会收到转推提醒。
  * 当白名单用户**评论或引用**别人的内容时，你会收到一条组合消息，其中既包含他的评论，也包含了被他评论的原始内容，让你一目了然，无需跳转查看。