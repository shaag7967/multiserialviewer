from PySide6.QtWidgets import QProxyStyle, QStyle


class ProxyStyle(QProxyStyle):
    def subElementRect(self, element, opt, widget=None):
        if element == QStyle.SubElement.SE_ItemViewItemCheckIndicator and not opt.text:
            rect = super().subElementRect(element, opt, widget)
            rect.moveCenter(opt.rect.center())
            return rect
        return super().subElementRect(element, opt, widget)
