from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal
from .validators import validar_cedula_ecuatoriana, validar_ruc_ecuatoriano, validar_telefono


class UsuarioManager(BaseUserManager):
    """Administrador personalizado para autenticación mediante correo electrónico."""

    def create_user(self, email, cedula, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        if not cedula:
            raise ValueError('La cédula es obligatoria.')

        email = self.normalize_email(email)
        user = self.model(email=email, cedula=cedula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, cedula, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, cedula, password, **extra_fields)


class Usuario(AbstractUser):
    """Modelo de usuario personalizado con atributos requeridos del sistema."""
    username = None
    cedula = models.CharField(
        'Cédula',
        max_length=10,
        unique=True,
        validators=[validar_cedula_ecuatoriana],
    )
    first_name = models.CharField('Nombres', max_length=100)
    last_name = models.CharField('Apellidos', max_length=100)
    email = models.EmailField('Correo electrónico', unique=True)
    telefono = models.CharField('Teléfono', max_length=10, validators=[validar_telefono])
    fecha_nacimiento = models.DateField('Fecha de nacimiento')
    direccion = models.CharField('Dirección', max_length=255)
    activo = models.BooleanField('Activo', default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cedula', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'direccion']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.cedula})'


class ModeloBase(models.Model):
    """Clase base abstracta (POO) que centraliza auditoría y eliminado lógico."""
    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última actualización', auto_now=True)

    class Meta:
        abstract = True

    def eliminar_logico(self):
        self.activo = False
        self.save(update_fields=['activo', 'fecha_actualizacion'])


class Categoria(ModeloBase):
    """Mantenimiento relacionado 1: Clasificación de artículos."""
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Proveedor(ModeloBase):
    """Mantenimiento relacionado 2: Proveedores de artículos."""
    ruc = models.CharField('RUC', max_length=13, unique=True, validators=[validar_ruc_ecuatoriano])
    nombre = models.CharField('Razón social / Nombre', max_length=150)
    telefono = models.CharField('Teléfono', max_length=10, validators=[validar_telefono])
    correo = models.EmailField('Correo electrónico', unique=True)
    direccion = models.CharField('Dirección', max_length=255)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.ruc})'


class Articulo(ModeloBase):
    """Mantenimiento principal (núcleo): Artículos del inventario."""
    codigo = models.CharField('Código', max_length=30, unique=True)
    nombre = models.CharField('Nombre del artículo', max_length=150)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='articulos',
        verbose_name='Categoría',
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='articulos',
        verbose_name='Proveedor principal',
    )
    precio_unitario = models.DecimalField(
        'Precio unitario ($)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    stock_actual = models.PositiveIntegerField('Stock actual', default=0)
    stock_minimo = models.PositiveIntegerField('Stock mínimo', default=5)

    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    @property
    def bajo_stock(self):
        return self.stock_actual <= self.stock_minimo


class Entrada(ModeloBase):
    """Mantenimiento relacionado 3: Ingresos de stock al inventario."""
    numero_documento = models.CharField('N.º de documento', max_length=30, unique=True)
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='entradas',
        verbose_name='Artículo',
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='entradas',
        verbose_name='Proveedor',
    )
    cantidad = models.PositiveIntegerField('Cantidad ingresada', validators=[MinValueValidator(1)])
    costo_unitario = models.DecimalField(
        'Costo unitario ($)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    fecha_entrada = models.DateField('Fecha de entrada')
    observacion = models.TextField('Observación', blank=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entradas_registradas',
        verbose_name='Registrado por',
    )

    class Meta:
        verbose_name = 'Entrada'
        verbose_name_plural = 'Entradas'
        ordering = ['-fecha_entrada', '-id']

    def __str__(self):
        return f'Entrada {self.numero_documento} - {self.articulo.nombre}'

    @property
    def total(self):
        return self.cantidad * self.costo_unitario


class Salida(ModeloBase):
    """Mantenimiento relacionado 4: Egresos de stock del inventario."""
    MOTIVOS = [
        ('VENTA', 'Venta'),
        ('USO_INTERNO', 'Uso interno'),
        ('DEVOLUCION', 'Devolución a proveedor'),
        ('MERMA', 'Merma / Daño'),
    ]

    numero_documento = models.CharField('N.º de documento', max_length=30, unique=True)
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='salidas',
        verbose_name='Artículo',
    )
    cantidad = models.PositiveIntegerField('Cantidad retirada', validators=[MinValueValidator(1)])
    motivo = models.CharField('Motivo', max_length=20, choices=MOTIVOS, default='VENTA')
    fecha_salida = models.DateField('Fecha de salida')
    observacion = models.TextField('Observación', blank=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salidas_registradas',
        verbose_name='Registrado por',
    )

    class Meta:
        verbose_name = 'Salida'
        verbose_name_plural = 'Salidas'
        ordering = ['-fecha_salida', '-id']

    def __str__(self):
        return f'Salida {self.numero_documento} - {self.articulo.nombre}'