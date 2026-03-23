# استخدام سيرفر Nginx الخفيف لعرض الصفحات
FROM nginx:alpine

# نسخ ملف الواجهة إلى مجلد السيرفر الافتراضي
COPY index.html /usr/share/nginx/html/index.html

# فتح المنفذ 80 للمتصفح
EXPOSE 80
