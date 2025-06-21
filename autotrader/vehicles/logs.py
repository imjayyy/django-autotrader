# from django.http import StreamingHttpResponse
# import time

# def stream_logs(request):
#     def event_stream():
#         log_path = "vehicles\livelogfile.log"  
#         last_size = 0

#         while True:
#             try:
#                 with open(log_path, "r") as f:
#                     f.seek(last_size)
#                     new_data = f.read()
#                     last_size = f.tell()
#                     if new_data:
#                         yield f"data: {new_data.strip()}\n\n"
#             except Exception as e:
#                 yield f"data: [ERROR] {str(e)}\n\n"
#             time.sleep(1)

#     return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
