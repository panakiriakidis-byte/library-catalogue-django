from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
from .forms import UploadExcelForm, CustomUserCreationForm, PersonForm
from .models import Person, UploadLog
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from .forms import PersonManualForm
from django.db.models.functions import Cast
from django.db.models import Func
from django.db.models import IntegerField, Value
from django.http import HttpResponse
from django.template.loader import render_to_string



def home(request):
    return render(request, 'home.html')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()
    
def clean_ari8mos(value):
    if pd.isna(value):
        return None
    try:
        return str(int(value))  # 115011.0 → "115011"
    except (ValueError, TypeError):
        return str(value).strip() 

@login_required
def show_people(request):
    people = (
        Person.objects
        .exclude(ari8mosEisagoghs__isnull=True)
        .exclude(ari8mosEisagoghs__exact='')
        .annotate(
            ari8mos_int=Cast('ari8mosEisagoghs', IntegerField())
        )
        .order_by('ari8mos_int')
    )

    return render(request, 'main/people.html', {'people': people})
@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)

        if form.is_valid():
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            
            # ✅ υπάρχοντα IDs στη βάση
            existing_ids = set(
                Person.objects.values_list('ari8mosEisagoghs', flat=True)
            )

            # 🔴 Νέο set για να εντοπίζει διπλότυπα μέσα στο ίδιο Excel
            seen_in_file = set()

            added = []
            skipped = []
            duplicates = []
            new_objects = []

            for index, row in df.iterrows():
                ari8mos = clean_ari8mos(row.get('ΑΡΙΘΜΟΣ ΕΙΣΑΓΩΓΗΣ'))

                if not ari8mos:
                    skipped.append({
                        'row': index + 2,
                        'reason': 'Missing ΑΡΙΘΜΟΣ ΕΙΣΑΓΩΓΗΣ'
                    })
                    continue

                # 🔴 DUPLICATE ΜΕΣΑ ΣΤΟ ΙΔΙΟ EXCEL
                if ari8mos in seen_in_file:
                    skipped.append({
                        'row': index + 2,
                        'reason': 'Duplicate ΑΡΙΘΜΟΣ ΕΙΣΑΓΩΓΗΣ inside Excel'
                    })
                    continue
                seen_in_file.add(ari8mos)

                # 🔴 DUPLICATE CHECK (existing_ids = βάση δεδομένων)
                if ari8mos in existing_ids:
                    existing_person = Person.objects.filter(ari8mosEisagoghs=ari8mos).first()

                    if not existing_person:
                        # Ασφαλές insert
                        new_objects.append(Person(
                            ari8mosEisagoghs=ari8mos,
                            hmeromhnia_eis=clean(row.get('ΗΜΕΡΟΜΗΝΙΑ ΕΙΣΑΓΩΓΗΣ')),
                            syggrafeas=clean(row.get('ΣΥΓΓΡΑΦΕΑΣ')),
                            koha=clean(row.get('ΣΥΓΓΡΑΦΕΑΣ KOHA')),
                            titlos=clean(row.get('ΤΙΤΛΟΣ')),
                            ekdoths=clean(row.get('ΕΚΔΟΤΗΣ')),
                            ekdosh=clean(row.get('ΕΚΔΟΣΗ')),
                            etosEkdoshs=clean(row.get('ΕΤΟΣ ΕΚΔΟΣΗΣ')),
                            toposEkdoshs=clean(row.get('ΤΟΠΟΣ  ΕΚΔΟΣΗΣ')),
                            sxhma=clean(row.get('ΣΧΗΜΑ')),
                            selides=clean(row.get('ΣΕΛΙΔΕΣ')),
                            tomos=clean(row.get('ΤΟΜΟΣ')),
                            troposPromPar=clean(row.get('ΤΡΟΠΟΣ ΠΡΟΜΗΘΕΙΑΣ ΠΑΡΑΤΗΡΗΣΕΙΣ')),
                            ISBN=clean(row.get('ISBN')),
                            sthlh1=clean(row.get('Στήλη1')),
                            sthlh2=clean(row.get('Στήλη2')),
                        ))
                        existing_ids.add(ari8mos)
                        continue

                    # Πραγματικό duplicate → αποθήκευση για resolve
                    duplicates.append({
                        "left": {
                            "ari8mos": existing_person.ari8mosEisagoghs,
                            "hmeromhnia_eis": existing_person.hmeromhnia_eis,
                            "syggrafeas": existing_person.syggrafeas,
                            "koha": existing_person.koha,
                            "titlos": existing_person.titlos,
                            "ekdoths": existing_person.ekdoths,
                            "ekdosh": existing_person.ekdosh,
                            "etosEkdoshs": existing_person.etosEkdoshs,
                            "toposEkdoshs": existing_person.toposEkdoshs,
                            "sxhma": existing_person.sxhma,
                            "selides": existing_person.selides,
                            "tomos": existing_person.tomos,
                            "troposPromPar": existing_person.troposPromPar,
                            "ISBN": existing_person.ISBN,
                            "sthlh1": existing_person.sthlh1,
                            "sthlh2": existing_person.sthlh2,
                        },
                        "right": {
                            "ari8mos": ari8mos,
                            "hmeromhnia_eis": clean(row.get('ΗΜΕΡΟΜΗΝΙΑ ΕΙΣΑΓΩΓΗΣ')),
                            "syggrafeas": clean(row.get('ΣΥΓΓΡΑΦΕΑΣ')),
                            "koha": clean(row.get('ΣΥΓΓΡΑΦΕΑΣ KOHA')),
                            "titlos": clean(row.get('ΤΙΤΛΟΣ')),
                            "ekdoths": clean(row.get('ΕΚΔΟΤΗΣ')),
                            "ekdosh": clean(row.get('ΕΚΔΟΣΗ')),
                            "etosEkdoshs": clean(row.get('ΕΤΟΣ ΕΚΔΟΣΗΣ')),
                            "toposEkdoshs": clean(row.get('ΤΟΠΟΣ  ΕΚΔΟΣΗΣ')),
                            "sxhma": clean(row.get('ΣΧΗΜΑ')),
                            "selides": clean(row.get('ΣΕΛΙΔΕΣ')),
                            "tomos": clean(row.get('ΤΟΜΟΣ')),
                            "troposPromPar": clean(row.get('ΤΡΟΠΟΣ ΠΡΟΜΗΘΕΙΑΣ ΠΑΡΑΤΗΡΗΣΕΙΣ')),
                            "ISBN": clean(row.get('ISBN')),
                            "sthlh1": clean(row.get('Στήλη1')),
                            "sthlh2": clean(row.get('Στήλη2')),
                        },
                    })
                    continue

                # ✅ SAFE INSERT
                new_objects.append(Person(
                    ari8mosEisagoghs=ari8mos,
                    hmeromhnia_eis=clean(row.get('ΗΜΕΡΟΜΗΝΙΑ ΕΙΣΑΓΩΓΗΣ')),
                    syggrafeas=clean(row.get('ΣΥΓΓΡΑΦΕΑΣ')),
                    koha=clean(row.get('ΣΥΓΓΡΑΦΕΑΣ KOHA')),
                    titlos=clean(row.get('ΤΙΤΛΟΣ')),
                    ekdoths=clean(row.get('ΕΚΔΟΤΗΣ')),
                    ekdosh=clean(row.get('ΕΚΔΟΣΗ')),
                    etosEkdoshs=clean(row.get('ΕΤΟΣ ΕΚΔΟΣΗΣ')),
                    toposEkdoshs=clean(row.get('ΤΟΠΟΣ  ΕΚΔΟΣΗΣ')),
                    sxhma=clean(row.get('ΣΧΗΜΑ')),
                    selides=clean(row.get('ΣΕΛΙΔΕΣ')),
                    tomos=clean(row.get('ΤΟΜΟΣ')),
                    troposPromPar=clean(row.get('ΤΡΟΠΟΣ ΠΡΟΜΗΘΕΙΑΣ ΠΑΡΑΤΗΡΗΣΕΙΣ')),
                    ISBN=clean(row.get('ISBN')),
                    sthlh1=clean(row.get('Στήλη1')),
                    sthlh2=clean(row.get('Στήλη2')),
                ))
                existing_ids.add(ari8mos)

                added.append({
                    'ari8mos': ari8mos,
                    'titlos': clean(row.get('ΤΙΤΛΟΣ')),
                    'syggrafeas': clean(row.get('ΣΥΓΓΡΑΦΕΑΣ')),
                })
           
            Person.objects.bulk_create(new_objects, batch_size=1000)

            # ✅ Store duplicates for next step
            request.session['duplicates'] = duplicates

            # ✅ Log upload
            UploadLog.objects.create(
                user=request.user,
                filename=excel_file.name,
                rows_added=len(new_objects),
                rows_updated=0,
            )

            total_records = Person.objects.count()

            return render(request, 'upload_result.html', {
                'added_count': len(new_objects),
                'duplicate_count': len(duplicates),
                'skipped_count': len(skipped),
                'total_records': total_records,
            })

    else:
        form = UploadExcelForm()

    return render(request, 'upload_excel.html', {'form': form})

# ———————————————— Υπόλοιπες view functions παραμένουν ίδιες ————————————————
@login_required
def resolve_duplicates(request):
    duplicates = request.session.get('duplicates', [])

    if not duplicates:
        return render(
             request,
            'main/duplicates_done.html'  
        )
    
    current = duplicates[0]
    return render(request, 'main/duplicates.html', {'duplicates': duplicates})

@login_required
def handle_duplicate(request):
    if request.method != "POST":
        return redirect("resolve_duplicates")

    ari8mos = request.POST.get("ari8mos")
    action = request.POST.get("action")

    if not ari8mos or not action:
        return redirect("resolve_duplicates")

    duplicates = request.session.get("duplicates", [])

    # ΒΡΙΣΚΟΥΜΕ ΤΟ ΣΥΓΚΕΚΡΙΜΕΝΟ DUPLICATE
    dup = next(
        (d for d in duplicates if str(d["left"]["ari8mos"]) == str(ari8mos)),
        None
    )

    if not dup:
        return redirect("resolve_duplicates")

    # ΑΦΑΙΡΟΥΜΕ ΜΟΝΟ ΑΥΤΟ ΠΟΥ ΠΑΤΗΘΗΚΕ
    duplicates.remove(dup)
    request.session["duplicates"] = duplicates

    if action == "edit":
        return redirect(
            f"{reverse('edit_person', args=[ari8mos])}?next=duplicates"
        )

    # action == "skip"
    return redirect("resolve_duplicates")


@login_required
def skip_all_duplicates(request):
    if request.method == "POST":
        request.session['duplicates'] = []
        return redirect('show_people')
    return redirect('resolve_duplicates')

@login_required
def edit_person(request, pk):
    person = get_object_or_404(Person, pk=pk)
    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, "Record updated successfully.")
            if next_url == 'duplicates':
                return redirect('resolve_duplicates')
            return redirect('show_people')
    else:
        form = PersonForm(instance=person)

    return render(request, 'main/edit_person.html', {'form': form, 'person': person})

class RegexpReplace(Func):
    function = 'REGEXP_REPLACE'
    arity = 3

@login_required
def add_person(request):
    last_number = (
        Person.objects
        .exclude(ari8mosEisagoghs__isnull=True)
        .exclude(ari8mosEisagoghs__exact='')
        .annotate(
            clean_num=Cast(
                RegexpReplace(
                    'ari8mosEisagoghs',
                    Value(r'\..*$'),
                    Value('')
                ),
                IntegerField()
            )
        )
        .order_by('-clean_num')
        .values_list('clean_num', flat=True)
        .first()
    )

    next_number = (last_number or 0) + 1

    # ✅ FLAG ΑΠΟ REDIRECT
    submitted = request.GET.get("submitted") == "1"

    if request.method == 'POST':
        form = PersonManualForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.ari8mosEisagoghs = str(next_number)
            person.save()

            # ✅ POST → REDIRECT → GET
            return redirect(f"{reverse('add_person')}?submitted=1")
    else:
        form = PersonManualForm()

    return render(
        request,
        'main/add_person.html',
        {
            'form': form,
            'next_number': next_number,
            'submitted': submitted,
        }
    )

