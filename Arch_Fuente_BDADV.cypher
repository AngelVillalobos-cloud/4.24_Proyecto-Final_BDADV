MERGE (d:Dept {dname: "CONTABILIDAD"}) SET d.loc = "CIUDAD DE MEXICO", d.deptno = 10;
MERGE (d:Dept {dname: "INVESTIGACION"}) SET d.loc = "GUADALAJARA", d.deptno = 20;
MERGE (d:Dept {dname: "VENTAS"}) SET d.loc = "MONTERREY", d.deptno = 30;
MERGE (d:Dept {dname: "OPERACIONES"}) SET d.loc = "CHIHUAHUA", d.deptno = 40;

MATCH (d:Dept {dname: "CONTABILIDAD"}) CREATE (e:Emp {empno: 7839, ename: "REYES", job: "DIRECTOR", mgr: null, hiredate: "1981-11-17", sal: 5000.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7698, ename: "MENDOZA", job: "GERENTE", mgr: "REYES", hiredate: "1981-05-01", sal: 2850.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "CONTABILIDAD"}) CREATE (e:Emp {empno: 7782, ename: "HERRERA", job: "GERENTE", mgr: "REYES", hiredate: "1981-06-09", sal: 2450.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "INVESTIGACION"}) CREATE (e:Emp {empno: 7566, ename: "RAMIREZ", job: "GERENTE", mgr: "REYES", hiredate: "1981-04-02", sal: 2975.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "INVESTIGACION"}) CREATE (e:Emp {empno: 7788, ename: "TORRES", job: "ANALISTA", mgr: "RAMIREZ", hiredate: "1982-12-09", sal: 3000.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "INVESTIGACION"}) CREATE (e:Emp {empno: 7902, ename: "VARGAS", job: "ANALISTA", mgr: "RAMIREZ", hiredate: "1981-12-03", sal: 3000.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7499, ename: "GUTIERREZ", job: "VENDEDOR", mgr: "MENDOZA", hiredate: "1981-02-20", sal: 1600.0, comm: 300.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7521, ename: "CASTILLO", job: "VENDEDOR", mgr: "MENDOZA", hiredate: "1981-02-22", sal: 1250.0, comm: 500.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7654, ename: "MORALES", job: "VENDEDOR", mgr: "MENDOZA", hiredate: "1981-09-28", sal: 1250.0, comm: 1400.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7844, ename: "JIMENEZ", job: "VENDEDOR", mgr: "MENDOZA", hiredate: "1981-09-08", sal: 1500.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "INVESTIGACION"}) CREATE (e:Emp {empno: 7369, ename: "LOPEZ", job: "EMPLEADO", mgr: "VARGAS", hiredate: "1980-12-17", sal: 800.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "INVESTIGACION"}) CREATE (e:Emp {empno: 7876, ename: "GARCIA", job: "EMPLEADO", mgr: "TORRES", hiredate: "1983-01-12", sal: 1100.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "VENTAS"}) CREATE (e:Emp {empno: 7900, ename: "FLORES", job: "EMPLEADO", mgr: "MENDOZA", hiredate: "1981-12-03", sal: 950.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);
MATCH (d:Dept {dname: "CONTABILIDAD"}) CREATE (e:Emp {empno: 7934, ename: "CRUZ", job: "EMPLEADO", mgr: "HERRERA", hiredate: "1982-01-23", sal: 1300.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);

MERGE (d:Dept {dname: "VENTAS"}) ON CREATE SET d.loc = "MONTERREY" CREATE (e:Emp {empno: 9999, ename: "NUEVO", job: "ANALISTA", mgr: "REYES", hiredate: "2026-01-01", sal: 4000.0, comm: 0.0}) CREATE (e)-[:TRABAJA_EN]->(d);

MATCH (e:Emp)-[:TRABAJA_EN]->(d:Dept) RETURN e.empno AS empno, e.ename AS ename, e.job AS job, e.mgr AS mgr, e.hiredate AS hiredate, e.sal AS sal, e.comm AS comm, d.dname AS dname, d.loc AS loc ORDER BY e.ename;

MATCH (e:Emp)-[:TRABAJA_EN]->(d:Dept) WHERE e.ename CONTAINS "REYES" RETURN e.empno AS empno, e.ename AS ename, e.job AS job, e.mgr AS mgr, e.hiredate AS hiredate, e.sal AS sal, e.comm AS comm, d.dname AS dname, d.loc AS loc ORDER BY e.ename;

MATCH (e:Emp {ename: "NUEVO"}) SET e.job = COALESCE(null, e.job), e.mgr = COALESCE("MENDOZA", e.mgr), e.hiredate = COALESCE(null, e.hiredate), e.sal = COALESCE(4500.0, e.sal), e.comm = COALESCE(null, e.comm) RETURN e;

MATCH (e:Emp {ename: "NUEVO"}) DETACH DELETE e;