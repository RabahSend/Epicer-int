from django import forms

from orders.models import Distribution


class DistributionForm(forms.ModelForm):
	starts_at = forms.DateTimeField(
		label="Début",
		input_formats=["%Y-%m-%dT%H:%M"],
		widget=forms.DateTimeInput(
			attrs={"type": "datetime-local"},
			format="%Y-%m-%dT%H:%M",
		),
	)
	ends_at = forms.DateTimeField(
		label="Fin",
		required=False,
		input_formats=["%Y-%m-%dT%H:%M"],
		widget=forms.DateTimeInput(
			attrs={"type": "datetime-local"},
			format="%Y-%m-%dT%H:%M",
		),
	)
	location = forms.CharField(label="Lieu", max_length=255, required=False)

	class Meta:
		model = Distribution
		fields = ("starts_at", "ends_at", "location")

	def clean(self):
		cleaned_data = super().clean()
		starts_at = cleaned_data.get("starts_at")
		ends_at = cleaned_data.get("ends_at")
		if starts_at and ends_at and ends_at < starts_at:
			self.add_error(
				"ends_at",
				"La fin de la distribution ne peut pas être antérieure au début.",
			)
		return cleaned_data
