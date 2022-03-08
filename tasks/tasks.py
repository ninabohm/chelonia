from celery import shared_task


@shared_task(name='app.reverse')
def reverse(string):
    return string[::-1]
