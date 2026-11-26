from datetime import date
from django import forms
from django.db.models import Q
from .models import Usuario, Categoria, Proveedor, Articulo, Entrada, Salida
from .validators import validar_cedula_ecuatoriana, validar_ruc_ecuatoriano, validar_telefono


class EstiloFormularioMixin:
    """Mixin para asignar clases CSS consistentes a todos los campos."""

    def aplicar_estilos(self):
        for field in self.fields.values():
            clases_actuales = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'form-select {clases_actuales}'.strip()
            else:
                field.widget.attrs['class'] = f'form-input {clases_actuales}'.strip()


class LoginForm(EstiloFormularioMixin, forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'usuario@correo.com', 'autocomplete': 'email'}),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'autocomplete': 'current-password'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()


class RegistroUsuarioForm(EstiloFormularioMixin, forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres', 'id': 'id_password'}),
        error_messages={'min_length': 'La contraseña debe tener al menos 8 caracteres.'},
    )
    confirmar_password = forms.CharField(
        label='Confirmación de contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña', 'id': 'id_confirmar_password'}),
    )

    class Meta:
        model = Usuario
        fields = [
            'cedula',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'fecha_nacimiento',
            'direccion',
        ]
        labels = {
            'cedula': 'Cédula',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'direccion': 'Dirección',
        }
        widgets = {
            'cedula': forms.TextInput(attrs={'maxlength': '10', 'placeholder': 'Ej. 0912345678'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ej. Carlos Andrés'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Ej. Mendoza Vera'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'maxlength': '10', 'placeholder': 'Ej. 0991234567'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Av. Principal y Calle Secundaria'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()
        for field in self.fields.values():
            field.required = True

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula', '').strip()
        validar_cedula_ecuatoriana(cedula)
        if Usuario.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con esta cédula.', code='unique')
        return cedula

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con este correo electrónico.', code='unique')
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        validar_telefono(telefono)
        return telefono

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            hoy = date.today()
            if fecha >= hoy:
                raise forms.ValidationError('La fecha de nacimiento debe ser anterior a la fecha actual.')
            edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
            if edad < 15:
                raise forms.ValidationError('El usuario debe tener al menos 15 años.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')

        if password and confirmar and password != confirmar:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class CategoriaForm(EstiloFormularioMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['codigo', 'nombre', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. CAT-001'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Electrónica'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        qs = Categoria.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una categoría con este código.', code='unique')
        return codigo

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        qs = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una categoría con este nombre.', code='unique')
        return nombre


class ProveedorForm(EstiloFormularioMixin, forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['ruc', 'nombre', 'telefono', 'correo', 'direccion']
        widgets = {
            'ruc': forms.TextInput(attrs={'maxlength': '13', 'placeholder': 'Ej. 0991234567001'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Distribuidora Central S.A.'}),
            'telefono': forms.TextInput(attrs={'maxlength': '10', 'placeholder': 'Ej. 042123456'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'ventas@proveedor.com'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección comercial'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()

    def clean_ruc(self):
        ruc = self.cleaned_data['ruc'].strip()
        validar_ruc_ecuatoriano(ruc)
        qs = Proveedor.objects.filter(ruc=ruc)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un proveedor con este RUC.', code='unique')
        return ruc

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        qs = Proveedor.objects.filter(correo__iexact=correo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un proveedor con este correo electrónico.', code='unique')
        return correo


class ArticuloForm(EstiloFormularioMixin, forms.ModelForm):
    class Meta:
        model = Articulo
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'proveedor',
            'precio_unitario',
            'stock_actual',
            'stock_minimo',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. ART-001'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Monitor LED 24 pulgadas'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Especificaciones del artículo'}),
            'precio_unitario': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'stock_actual': forms.NumberInput(attrs={'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                Q(activo=True) | Q(pk=self.instance.categoria_id)
            )
            self.fields['proveedor'].queryset = Proveedor.objects.filter(
                Q(activo=True) | Q(pk=self.instance.proveedor_id)
            )
        else:
            self.fields['categoria'].queryset = Categoria.objects.filter(activo=True)
            self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)
        self.aplicar_estilos()

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        qs = Articulo.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un artículo con este código.', code='unique')
        return codigo

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is not None and precio <= 0:
            raise forms.ValidationError('El precio unitario debe ser mayor a 0.')
        return precio


class EntradaForm(EstiloFormularioMixin, forms.ModelForm):
    class Meta:
        model = Entrada
        fields = [
            'numero_documento',
            'articulo',
            'proveedor',
            'cantidad',
            'costo_unitario',
            'fecha_entrada',
            'observacion',
        ]
        widgets = {
            'numero_documento': forms.TextInput(attrs={'placeholder': 'Ej. ENT-2026-001'}),
            'cantidad': forms.NumberInput(attrs={'min': '1'}),
            'costo_unitario': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'fecha_entrada': forms.DateInput(attrs={'type': 'date'}),
            'observacion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalle del ingreso'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['articulo'].queryset = Articulo.objects.filter(
                Q(activo=True) | Q(pk=self.instance.articulo_id)
            )
            self.fields['proveedor'].queryset = Proveedor.objects.filter(
                Q(activo=True) | Q(pk=self.instance.proveedor_id)
            )
        else:
            self.fields['articulo'].queryset = Articulo.objects.filter(activo=True)
            self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)
        self.aplicar_estilos()

    def clean_numero_documento(self):
        doc = self.cleaned_data['numero_documento'].strip().upper()
        qs = Entrada.objects.filter(numero_documento__iexact=doc)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una entrada con este número de documento.', code='unique')
        return doc

    def clean_fecha_entrada(self):
        fecha = self.cleaned_data.get('fecha_entrada')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de entrada no puede ser futura.')
        return fecha


class SalidaForm(EstiloFormularioMixin, forms.ModelForm):
    class Meta:
        model = Salida
        fields = [
            'numero_documento',
            'articulo',
            'cantidad',
            'motivo',
            'fecha_salida',
            'observacion',
        ]
        widgets = {
            'numero_documento': forms.TextInput(attrs={'placeholder': 'Ej. SAL-2026-001'}),
            'cantidad': forms.NumberInput(attrs={'min': '1'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
            'observacion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalle de la salida'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['articulo'].queryset = Articulo.objects.filter(
                Q(activo=True) | Q(pk=self.instance.articulo_id)
            )
        else:
            self.fields['articulo'].queryset = Articulo.objects.filter(activo=True)
        self.aplicar_estilos()

    def clean_numero_documento(self):
        doc = self.cleaned_data['numero_documento'].strip().upper()
        qs = Salida.objects.filter(numero_documento__iexact=doc)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una salida con este número de documento.', code='unique')
        return doc

    def clean_fecha_salida(self):
        fecha = self.cleaned_data.get('fecha_salida')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de salida no puede ser futura.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        articulo = cleaned_data.get('articulo')
        cantidad = cleaned_data.get('cantidad')

        if articulo and cantidad:
            stock_disponible = articulo.stock_actual
            if self.instance.pk and self.instance.articulo_id == articulo.pk:
                stock_disponible += self.instance.cantidad

            if cantidad > stock_disponible:
                self.add_error(
                    'cantidad',
                    f'Stock insuficiente. Disponible para este artículo: {stock_disponible} unidades.',
                )
        return cleaned_data