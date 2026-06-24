export function SiteFooter() {
  return (
    <footer
      aria-label="网站备案信息"
      className="border-t border-border bg-background/95 px-6 py-6 text-sm text-muted-foreground"
    >
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-center gap-2 text-center">
        <p className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
          <span>Copyright © 2020 广州美太管理咨询有限公司 版权所有</span>
          <a
            href="http://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-primary transition-colors hover:text-warm-text"
          >
            粤ICP备18143723号
          </a>
        </p>

        <p className="text-xs text-muted-foreground/80">
          Guangzhou Meitai Management Consulting Co., Ltd. All Rights Reserved
        </p>
      </div>
    </footer>
  );
}
