from myapp.models import Message, Teacher, Parent

print(f"Total Messages: {Message.objects.count()}")
parent_msgs = Message.objects.filter(sender_role='Parent')
print(f"Parent Messages Count: {parent_msgs.count()}")
for msg in parent_msgs:
    print(f"From: {msg.sender_name}, To: {msg.recipient.username}, Msg: {msg.message}")

teachers = Teacher.objects.all()
print("\nTeachers:")
for t in teachers:
    print(f"Name: {t.name}, Username: {t.username}, ID: {t.id}")

parents = Parent.objects.all()
print("\nParents:")
for p in parents:
    print(f"Name: {p.name}, Username: {p.username}, ID: {p.id}")
