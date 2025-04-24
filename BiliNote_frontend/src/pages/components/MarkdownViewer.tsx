import { useState, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import { Button } from "@/components/ui/button"
import { Copy, Download, FileText, ArrowRight, Clock } from "lucide-react"
import { toast } from "sonner" // 你可以换成自己的通知组件
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { solarizedlight as codeStyle } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import 'github-markdown-css/github-markdown-light.css'
import {FC} from 'react'
import Loading from "@/components/Lottie/Loading.tsx";
import Idle from "@/components/Lottie/Idle.tsx";
import {useTaskStore, Timings} from "@/store/taskStore";
interface MarkdownViewerProps {
    content: string
    status: 'idle' | 'loading' | 'success'
}

// 格式化时间为 mm:ss 格式
const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

const MarkdownViewer: FC<MarkdownViewerProps> = ({ content, status }) => {
    const [copied, setCopied] = useState(false)
    const [elapsedTime, setElapsedTime] = useState(0)
    const getCurrentTask = useTaskStore.getState().getCurrentTask
    const currentTask = getCurrentTask()

    // 计时器逻辑 - 仅在加载状态下运行
    useEffect(() => {
        let timer: number | null = null;

        if (status === 'loading') {
            // 启动计时器
            timer = window.setInterval(() => {
                setElapsedTime(prev => prev + 1);
            }, 1000);
        } else {
            // 重置计时器
            setElapsedTime(0);
        }

        return () => {
            if (timer) {
                clearInterval(timer);
            }
        };
    }, [status]);
    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(content)
            setCopied(true)
            toast.success("已复制到剪贴板")
            setTimeout(() => setCopied(false), 2000)
        } catch (e) {
            toast.error(`复制失败${e}`)
            toast.error("复制失败",e)
        }
    }

    const handleDownload = () => {
        const currentTask=getCurrentTask()
        const currentTaskName=currentTask?.audioMeta.title
        const blob = new Blob([content], { type: "text/markdown;charset=utf-8" })
        const link = document.createElement("a")
        link.href = URL.createObjectURL(blob)
        link.download = `${currentTaskName}.md`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }
    if (status === 'loading') {
        return (
            <div className="w-full h-screen flex flex-col justify-center items-center text-neutral-500 space-y-4">
                <Loading className='h-5 w-5' />
                <div className="text-center text-sm">
                    <p className="text-lg font-bold">正在生成笔记，请稍候…</p>
                    <div className="mt-2 flex items-center justify-center gap-1 text-primary">
                        <Clock className="h-4 w-4" />
                        <span className="font-mono">{formatTime(elapsedTime)}</span>
                    </div>
                    <p className="mt-2 text-xs text-neutral-500">这可能需要几分钟时间，取决于视频长度</p>
                </div>
            </div>
        )
    }
    else if (status === 'idle'){
        return (
            <div className="w-full h-screen flex flex-col justify-center items-center text-neutral-500 space-y-3">

                    <Idle ></Idle>

                <div className="text-center">
                    <p className="text-lg font-bold">输入视频链接并点击“生成笔记”</p>
                    <p className="mt-2 text-xs text-neutral-500">支持哔哩哔哩、YouTube 等视频平台</p>
                </div>
            </div>

        )
    }

    return (
        <div className="w-full h-full flex flex-col">
            {/* 顶部操作栏 */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-neutral-900 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    笔记内容
                </h2>
                <div className="flex items-center gap-2">
                    <Button onClick={handleCopy} variant="outline" size="sm">
                        <Copy className="w-4 h-4 mr-1" />
                        {copied ? "已复制" : "复制"}
                    </Button>
                    <Button onClick={handleDownload} variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        导出 Markdown
                    </Button>
                </div>
            </div>

            {/* 计时信息显示 */}
            {currentTask?.timings && currentTask.timings.total > 0 && (
                <div className="bg-gray-50 p-3 rounded-md mb-4 text-sm border border-gray-200">
                    <div className="flex items-center gap-1 text-gray-700 mb-2">
                        <Clock className="h-4 w-4 text-primary" />
                        <span className="font-medium">笔记生成耗时</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        <div className="flex flex-col">
                            <span className="text-xs text-gray-500">总耗时</span>
                            <span className="font-mono font-medium">{currentTask.timings.total}秒</span>
                        </div>
                        {currentTask.timings.audio_download > 0 && (
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500">音频下载</span>
                                <span className="font-mono">{currentTask.timings.audio_download}秒</span>
                            </div>
                        )}
                        {currentTask.timings.video_download > 0 && (
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500">视频下载</span>
                                <span className="font-mono">{currentTask.timings.video_download}秒</span>
                            </div>
                        )}
                        {currentTask.timings.transcription > 0 && (
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500">音频转写</span>
                                <span className="font-mono">{currentTask.timings.transcription}秒</span>
                            </div>
                        )}
                        {currentTask.timings.gpt_summary > 0 && (
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500">AI 总结</span>
                                <span className="font-mono">{currentTask.timings.gpt_summary}秒</span>
                            </div>
                        )}
                        {currentTask.timings.post_processing > 0 && (
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500">后处理</span>
                                <span className="font-mono">{currentTask.timings.post_processing}秒</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 滚动容器 */}

            <div className='overflow-y-auto'>
                {
                    content && content!='loading' || content!='empty'?(
                        <div className="markdown-body flex-1  bg-white">  <ReactMarkdown

                            components={{
                                code({ node, inline, className, children, ...props }) {
                                    const match = /language-(\w+)/.exec(className || '')
                                    const codeContent = String(children).replace(/\n$/, '')

                                    if (!inline && match) {
                                        return (
                                            <div className="relative group">
                                                <SyntaxHighlighter
                                                    style={codeStyle}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                >
                                                    {codeContent}
                                                </SyntaxHighlighter>
                                                <button
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(codeContent)
                                                        toast.success("代码已复制")
                                                    }}
                                                    className="absolute top-2 right-2 hidden group-hover:flex items-center gap-1 text-xs px-2 py-1 bg-white/70 border border-gray-300 rounded hover:bg-white shadow-sm transition"
                                                >
                                                    <Copy className="w-3 h-3" />
                                                    复制
                                                </button>
                                            </div>
                                        )
                                    }

                                    return (
                                        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                                            {children}
                                        </code>
                                    )
                                }
                            }}
                        >
                            {content}
                        </ReactMarkdown></div>
                    ):(
                        <div className='w-full h-screen flex justify-center items-center'>
                           <div className='w-[300px] flex-col justify-items-center '>
                               <div className="w-16 h-16 bg-primary-light rounded-full flex items-center justify-center mb-4">
                                    <ArrowRight className="h-8 w-8 text-primary" />
                               </div>
                               <p className="text-neutral-600 mb-2">输入视频链接并点击"生成笔记"按钮</p>
                               <p className="text-xs text-neutral-500">支持哔哩哔哩、YouTube等视频网站</p>
                           </div>
                        </div>
                    )
                }
            </div>
            {/*<div className="markdown-body flex-1 overflow-y-auto bg-white">*/}
            {/*    {content ? (*/}
            {/*      */}
            {/*    ) : (*/}
            {/*        <>*/}
            {/*            <div className="w-16 h-16 bg-primary-light rounded-full flex items-center justify-center mb-4">*/}
            {/*                <ArrowRight className="h-8 w-8 text-primary" />*/}
            {/*            </div>*/}
            {/*            <p className="text-neutral-600 mb-2">输入视频链接并点击"生成笔记"按钮</p>*/}
            {/*            <p className="text-xs text-neutral-500">支持哔哩哔哩、YouTube、腾讯视频和爱奇艺</p>*/}
            {/*        </>*/}
            {/*    )}*/}
            {/*</div>*/}
        </div>
    )
}

export default MarkdownViewer
