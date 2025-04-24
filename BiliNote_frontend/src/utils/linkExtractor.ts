/**
 * 从文本中提取抖音、哔哩哔哩或YouTube链接
 * @param text 可能包含视频链接的文本
 * @returns 提取出的链接，如果没有找到则返回原文本
 */
export function extractVideoLink(text: string): string {
  if (!text) return '';
  
  // 抖音链接正则表达式 (匹配 v.douyin.com/xxxx/ 格式)
  const douyinRegex = /(https?:\/\/v\.douyin\.com\/[a-zA-Z0-9]+\/?)/i;
  
  // 哔哩哔哩链接正则表达式
  const bilibiliRegex = /(https?:\/\/(?:www\.)?bilibili\.com\/video\/[a-zA-Z0-9]+\/?)/i;
  
  // YouTube链接正则表达式
  const youtubeRegex = /(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]+\/?)/i;
  
  // 尝试匹配各种链接
  const douyinMatch = text.match(douyinRegex);
  const bilibiliMatch = text.match(bilibiliRegex);
  const youtubeMatch = text.match(youtubeRegex);
  
  // 返回找到的第一个链接，优先级：抖音 > 哔哩哔哩 > YouTube
  if (douyinMatch) return douyinMatch[0];
  if (bilibiliMatch) return bilibiliMatch[0];
  if (youtubeMatch) return youtubeMatch[0];
  
  // 如果没有找到任何链接，返回原文本
  return text;
}

/**
 * 从文本中识别视频平台类型
 * @param url 视频链接
 * @returns 平台类型：'douyin', 'bilibili', 'youtube' 或 null
 */
export function detectPlatform(url: string): string | null {
  if (!url) return null;
  
  if (url.includes('douyin.com') || url.includes('v.douyin.com')) {
    return 'douyin';
  } else if (url.includes('bilibili.com')) {
    return 'bilibili';
  } else if (url.includes('youtube.com') || url.includes('youtu.be')) {
    return 'youtube';
  }
  
  return null;
}
