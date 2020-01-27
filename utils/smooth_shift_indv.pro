PRO smooth_shift_indv

; this code will read in a GBTIDL FITS file then smooth the data either 
; using gconvol+resample (to get arbitrary resolution), and then
; will shift the data, with gshift, to line up the final channels with other
; datasets. The user specifies the source, outfile name, and kernel construction
; The kernel should have the format of [0.7,1.,1.,1.,0.7]

;; unpack user arguments passed from python wrapper
args = COMMAND_LINE_ARGS()
fileName  = args[0]
sname = args[1]
outfile = args[2]

;; construct Gaussian kernel
for i=3, N_ELEMENTS(args) - 1 DO BEGIN
	kernel = APPEND(kernel, args[i])
ENDFOR

allscans=get_scan_numbers(source=sname,procedure='*Map')

fileout,outfile

freeze
for s=0,n_elements(allscans)-1 do begin
    info=scan_info(allscans(s))
    nint=info.n_integrations
    for i=0,nint-1 do begin
	for p=0,1 do begin
	    print, allscans(s),i,p
	    get,scan=allscans(s),int=i,plnum=p
	    if keyword_set(box) then begin
		boxcar,box,/decimate 
	    endif
	    if keyword_set(kernel)then begin
		gconvol,kernel/total(kernel)
		resample,!g.s[0].frequency_interval*total(kernel)
	    endif
	    if keyword_set(cshift) then begin
		gshift,cshift,/spline
	    endif
	    keep
	endfor
   endfor
endfor

unfreeze

end
