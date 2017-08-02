import hbv96 as mcd


md = mcd.HBV96()

md.par['area'] = 33.5

md.par['tfac'] = 24

md.config['file_path'] = '/home/niko/Documents/UNESCO-IHE/Model/HBV96/all_data.csv'

md.config['header'] = 0

md.config['separator'] = ','

md.config['obj_fun'] = md._rmse

md.config['init_guess'] = None

md.config['fun_name'] = 'RMSE'

md.config['warm_up'] = 10

md.config['verbose'] = True

md.config['minimise'] = True

md.config['tol'] = 0.0001

md.extract_to_dict()

md.DEF_q0 = 0.183

md.calibrate()

print md.par

md.generate_csv()
