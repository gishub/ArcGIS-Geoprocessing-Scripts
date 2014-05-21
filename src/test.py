import datetime, bisect
from netCDF4 import Dataset
from dateutil.relativedelta import relativedelta

def GetDateBins(dateFrom, dateTo, dateInterval):
    '''Gets DateBins from the start date to the end date - including the end date'''
    diff = relativedelta(dateTo, dateFrom)
    if dateInterval == "day":
        totaldays = ((d2 - d1).days) + 1
        dates = [dateFrom + relativedelta(days=i) for i in range(totaldays)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_d" + d.strftime("%j")} for d in dates]
    elif dateInterval == "month":
        totalmonths = (diff.years * 12 + diff.months) + 1
        dates = [dateFrom + relativedelta(months=i) for i in range(totalmonths)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_m" + str(d.month).zfill(2)} for d in dates]
    elif dateInterval == "year":
        totalyears = diff.years + 1
        dates = [dateFrom + relativedelta(years=i) for i in range(totalyears)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year)} for d in dates]
    elif dateInterval[:3] == "lta":
        interval = int(dateInterval[3:])
        totalCount = (diff.years / interval) + 1
        dates = [dateFrom + relativedelta(years=(i * interval)) for i in range(totalCount)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_yy" + str(d.year) + "_" + str(d.year + interval)} for d in dates]
    return dateBins

def GetNetCDFOrdinals(data, startDate):
    '''Returns an array of proleptic gregrian dates for the passed netcdf'''
    t = data.variables['time']
    if t.size == 0:
        return ""
    elif  t.size == 141:
        return [(startDate + relativedelta(years=i)).toordinal() for i in range(len(t))]
    elif t.size == 564:
        return [(startDate + relativedelta(years=i)).toordinal() for i in range(len(t))]
    elif t.size == 1692:
        return [(startDate + relativedelta(months=i)).toordinal() for i in range(len(t))]
    elif t.size > 1692:
        return [(startDate + relativedelta(days=i)).toordinal() for i in range(len(t))]
    
d1 = datetime.datetime(1960, 1, 1)
d2 = datetime.datetime(2100, 1, 1)
dateInterval = "lta35"
dateBins = GetDateBins(d1, d2, dateInterval)
data = Dataset('D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/ClimAf_1_1960-2100_lpjg_can_wfdei_somd_B1_etotx_sea_teco_ir.nc')
ordinals = GetNetCDFOrdinals(data, d1)
indices = [bisect.bisect_left(ordinals, bin['ordinal']) for bin in dateBins]
slices = [{"start":indices[i - 1], "end":indices[i] - 1,"label":dateBins[i-1]['label']} for i in range(1, len(indices))]
print slices
